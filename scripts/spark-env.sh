#!/usr/bin/env zsh
# A sourcer avant toute commande Spark : ne telecharge ni n'installe rien.
# Spark 3.5 / Hadoop de cette demonstration necessite Java 17 a 23 ; le JDK 26
# du poste retire Subject.getSubject(), encore appele par Hadoop.

set -eu

if command -v brew >/dev/null 2>&1 && [ -d "$(brew --prefix openjdk@17)/libexec/openjdk.jdk/Contents/Home" ]; then
  export JAVA_HOME="$(brew --prefix openjdk@17)/libexec/openjdk.jdk/Contents/Home"
elif [ -d "/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home" ]; then
  export JAVA_HOME="/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"
else
  echo "Java 17 introuvable. Installer/preparer un JDK 17 local avant la demonstration Spark." >&2
  return 1 2>/dev/null || exit 1
fi

export PATH="$JAVA_HOME/bin:$PATH"
java -version 2>&1 | head -n 1
