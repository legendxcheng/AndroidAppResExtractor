import subprocess

adb_path = "./adb.exe"
device = "127.0.0.1:7555"

# 测试正确的su调用方式
cmd_str = 'find /data/app/ -maxdepth 2 -type d -name "com.chenyou.slsy.yofun.mumu*"'

print("测试正确方式: 整个su命令作为一个参数")
print(f"内部命令: {cmd_str}")

# 将 'su -c' 和命令组合成一个完整的shell参数
full_cmd = f"su -c '{cmd_str}'"
print(f"完整命令: {full_cmd}")

result = subprocess.run(
    [adb_path, '-s', device, 'shell', full_cmd],
    capture_output=True,
    text=True
)

print(f"stdout: [{result.stdout}]")
print(f"stderr: [{result.stderr}]")
print(f"returncode: {result.returncode}")
print()

# 测试2: ls命令
path = "/data/data/com.chenyou.slsy.yofun.mumu/"
cmd_str = f'ls {path}'
full_cmd = f"su -c '{cmd_str}'"

print("测试2: ls命令")
print(f"完整命令: {full_cmd}")

result = subprocess.run(
    [adb_path, '-s', device, 'shell', full_cmd],
    capture_output=True,
    text=True
)

print(f"stdout前100字符: [{result.stdout[:100]}]")
print(f"returncode: {result.returncode}")
