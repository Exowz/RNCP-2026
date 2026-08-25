#!/usr/bin/env zsh
# A sourcer avant toute commande Spark : ne telecharge ni n'installe rien.
# Spark 3.5 / Hadoop de cette demonstration necessite Java 17 a 23 ; le JDK 26
# du poste retire Subject.getSubject(), encore appele par Hadoop.

set -eu

typeset -a candidats_java
candidats_java=(
  "${JAVA_HOME:-}"
  "/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"
  "/usr/local/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"
)

if [ -x "/usr/libexec/java_home" ]; then
  candidats_java+=("$(/usr/libexec/java_home -v 17 2>/dev/null)")
fi

unset JAVA_HOME
for candidat_java in "${candidats_java[@]}"; do
  if [ -x "$candidat_java/bin/java" ] \
    && "$candidat_java/bin/java" -version 2>&1 | head -n 1 | grep -q 'version "17\.'; then
    export JAVA_HOME="$candidat_java"
    break
  fi
done

if [ -z "${JAVA_HOME:-}" ]; then
  echo "Java 17 introuvable. Installer/preparer un JDK 17 local avant la demonstration Spark." >&2
  return 1 2>/dev/null || exit 1
fi

export PATH="$JAVA_HOME/bin:$PATH"
java -version 2>&1 | head -n 1
