#!/usr/bin/env bash

if [ ! -d "/ql" ];then
  root=/jd
else
  root=/ql
fi

dir_jbot=$root/jbot
dir_diybot=$root/repo/diybot
file_bot=$root/config/bot.json
file_botset=$root/config/botset.json
file_diybotset=$root/config/diybotset.json
url="https://ghproxy.com/https://github.com/Annyoo2021/mybot.git"

git_clone() {
    local url=$1
    local dir=$2
    local branch=$3
    [[ $branch ]] && local cmd="-b $branch "
    echo "开始克隆仓库 $url 到 $dir"
    git clone $cmd $url $dir
    exit_status=$?
}

backup() {
  if [ ! -d $root/repo/backup ]; then
    mkdir $root/repo/backup
  fi
  mkdir $root/repo/backup/$(date +\%m\%d\%H\%M)
  cp -rf $root/jbot/* $root/repo/backup/$(date +\%m\%d\%H\%M)
  rm -rf $root/jbot/*
  cd $root
}

env() {
  echo "1、安装bot依赖..."
  apk --no-cache add -f zlib-dev gcc jpeg-dev python3-dev musl-dev freetype-dev
  echo -e "bot依赖安装成功...\n"
  cd $root || exit
}

bot() {
  echo "2、下载bot所需文件..."
  if [ -d ${dir_diybot} ]; then
    rm -rf $dir_diybot
  fi
  git_clone ${url} ${dir_diybot} "main"
  if [ -f $dir_jbot/diy/user.py ]; then
    mv -f $dir_jbot/diy/user.py $dir_diybot/jbot/diy/
    echo "存在user.py, 不更新user.py"
  else
    rm -f $dir_diybot/jbot/diy/user.py
    echo "不存在user.py，或是首次安装，请安装完bot再单独安装user"
  fi
  if [ -d ${dir_jbot} ]; then
    backup
  fi

  if [ -f $dir_jbot/diy/diy.py ]; then
    rm -f $dir_diybot/jbot/diy/diy.py
  fi
  cp -rf $dir_diybot/jbot/* $dir_jbot
  echo -e "bot文件下载成功...\n"
  if [[ ! -f $file_bot ]]; then
    cp -f $dir_diybot/config/bot.json $root/config
  fi
  if [[ ! -f $file_botset ]]; then
    cp -f $dir_diybot/jbot/set.json $root/config
    mv -f $root/config/set.json $root/config/botset.json
  fi
  if [[ ! -f $file_diybotset ]]; then
    cp -f $dir_diybot/config/diybotset.json $root/config
  fi
  cd $root || exit
}

packages() {
  echo "3、安装python3依赖..."
  cd $dir_jbot || exit
  /usr/bin/python3 -m pip install --upgrade pip
  pip3 config set global.index-url https://mirrors.aliyun.com/pypi/simple/
  pip3  --no-cache-dir --default-timeout=100 install -r requirements.txt
  echo -e "python3依赖安装成功...\n"
  cd $root || exit
}

start() {
  echo "4、启动bot程序..."
  if [[ -z $(grep -E "123456789" $file_bot) ]]; then
    cd $dir_jbot || exit; pm2 start ecosystem.config.js
    echo "bot启动成功..."
  else
    echo "配置 $file_bot 后再次运行本程序即可启动机器人"
  fi
  cd $root || exit
}

main() {
  env
  bot
  packages
  start
}

main
exit 0
