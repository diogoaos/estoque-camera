#!/usr/bin/env sh

#
# Copyright © 2015-2021 the original authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Attempt to set APP_HOME
# Resolve links: $0 may be a link
PRG="$0"
# Need this for relative symlinks.
while [ -h "$PRG" ] ; do
    ls=`ls -ld "$PRG"`
    link=`expr "$ls" : '.*-> \(.*\)$'`
    if expr "$link" : '/.*' > /dev/null; then
        PRG="$link"
    else
        PRG=`dirname "$PRG"`"/$link"
    fi
done
SAVED="`pwd`"
cd "`dirname \"$PRG\"`/" >/dev/null
APP_HOME="`pwd -P`"
cd "$SAVED" >/dev/null

APP_NAME="Gradle"
APP_BASE_NAME=`basename "$0"`

# Add default JVM options here. You can also use JAVA_OPTS and GRADLE_OPTS to pass JVM options to this script.
DEFAULT_JVM_OPTS='"-Xmx64m" "-Xms64m"'

# Use the maximum available, or set MAX_FD != -1 to use that value.
MAX_FD="maximum"

warn () {
    echo "$*"
}

die () {
    echo
    echo "ERROR: $*"
    echo
    exit 1
}

# OS specific support (must be 'true' or 'false').
cygwin=false
msys=false
darwin=false
nonstop=false
case "`uname`" in
  CYGWIN* )
    cygwin=true
    ;;
  Darwin* )
    darwin=true
    ;;
  MINGW* )
    msys=true
    ;;
  NONSTOP* )
    nonstop=true
    ;;
esac

CLASSPATH=$APP_HOME/gradle/wrapper/gradle-wrapper.jar


# Determine the Java command to use to start the JVM.
if [ -n "$JAVA_HOME" ] ; then
    if [ -x "$JAVA_HOME/jre/sh/java" ] ; then
        # IBM's JDK on AIX uses strange locations for the executables
        JAVACMD="$JAVA_HOME/jre/sh/java"
    else
        JAVACMD="$JAVA_HOME/bin/java"
    fi
    if [ ! -x "$JAVACMD" ] ; then
        die "ERROR: JAVA_HOME is set to an invalid directory: $JAVA_HOME

Please set the JAVA_HOME variable in your environment to match the
location of your Java installation."
    fi
else
    JAVACMD="java"
    which java >/dev/null 2>&1 || die "ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH.

Please set the JAVA_HOME variable in your environment to match the
location of your Java installation."
fi

# Increase the maximum number of open files if necessary.
if ! "$cygwin" && ! "$darwin" && ! "$nonstop" ; then
    MAX_FD_LIMIT=`ulimit -H -n`
    if [ "$?" -eq 0 ] ; then
        if [ "$MAX_FD" = "maximum" -o "$MAX_FD" = "max" ] ; then
            # Use system's hard limit.
            #
            # Max open files ('ulimit -n') is increasing in steps like
            # 1024 -> 4096 -> 8192 -> 16384 -> 32768 -> 65536
            # considering it is not possible to predict what future value will
            # be encountered, MAX_FD_LIMIT is used directly here.
            MAX_FD="$MAX_FD_LIMIT"
        fi

        ulimit -n "$MAX_FD" # Use quotes around MAX_FD
        if [ "$?" -ne 0 ] ; then
            warn "Could not set maximum file descriptor limit: $MAX_FD"
        fi
    else
        warn "Could not query maximum file descriptor limit: $MAX_FD_LIMIT"
    fi
fi

# For Darwin, add options to specify how the application appears in the dock;
# also add a heap size option to support smaller terminal environments.
if "$darwin"; then
    GRADLE_OPTS="$GRADLE_OPTS \"-Xdock:name=$APP_NAME\" \"-Xdock:icon=$APP_HOME/media/gradle.icns\""
fi

# For Cygwin or MSYS, switch paths to Windows format before running java
if "$cygwin" || "$msys" ; then
    APP_HOME=`cygpath --path --mixed "$APP_HOME"`
    CLASSPATH=`cygpath --path --mixed "$CLASSPATH"`
    JAVACMD=`cygpath --unix "$JAVACMD"`

    # Convert arguments to Windows format
    # This is a simplified version for the known arguments.
    declare -a CONVERTED_ARGS
    for arg do
        case "$arg" in
            -D*=* | -P*=* )
                # Extract value after '='
                val=`expr "$arg" : '[^=]*=\(.*\)$'`
                # Convert value if it looks like a path
                if expr "$val" : '/.*' > /dev/null ; then
                    val=`cygpath --path --mixed "$val"`
                fi
                # Reconstruct the argument
                CONVERTED_ARGS+=("`expr "$arg" : '\([^=]*=\).*$'`$val")
                ;;
            --init-script|--project-cache-dir|--project-dir|--settings-file)
                CONVERTED_ARGS+=("$arg")
                # Peak next argument
                eval "next_arg=\${$((OPTIND))}"
                if [ -n "$next_arg" ] && ! expr "$next_arg" : '-.*' > /dev/null ; then
                     CONVERTED_ARGS+=("`cygpath --path --mixed "$next_arg"`")
                     OPTIND=$((OPTIND + 1)) # Increment OPTIND as we consumed next arg
                fi
                ;;
            *)
                CONVERTED_ARGS+=("$arg")
                ;;
        esac
    done
    set -- "${CONVERTED_ARGS[@]}"
fi

# Split up the JVM options only if DEFAULT_JVM_OPTS or JAVA_OPTS or GRADLE_OPTS is not empty.
JVM_OPTS=
if [ -n "$DEFAULT_JVM_OPTS" ] || [ -n "$JAVA_OPTS" ] || [ -n "$GRADLE_OPTS" ]; then
    JVM_OPTS="$DEFAULT_JVM_OPTS $JAVA_OPTS $GRADLE_OPTS"
fi

# Use exec to avoid startup process remaining during Gradle run
# Pass all script arguments to Gradle
exec "$JAVACMD" $JVM_OPTS -classpath "$CLASSPATH" org.gradle.wrapper.GradleWrapperMain "$@"
