cat << 'EOF' > ~/Downloads/Orbitronic/wait-for-db.sh
#!/bin/sh
# wait-for-db.sh

set -e

host="$1"
port="$2"
shift 2
cmd="$@"

until mysqladmin ping -h "$host" -P "$port" -u user -ppassword --silent; do
  echo "Waiting for MySQL to be ready..."
  sleep 2
done

echo "MySQL is up - executing command"
exec $cmd
EOF