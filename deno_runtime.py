import os
import shutil
import subprocess


class DenoRuntime:
    """Поиск и управление Deno JS-runtime для yt-dlp."""

    def __init__(self, deno_path=None):
        self.deno_path = self._find_deno(deno_path)
        self.is_available = self.check_deno()

    def _find_deno(self, manual_path):
        if manual_path:
            return manual_path

        # 1. Пробуем shutil.which
        found = shutil.which("deno")
        if found:
            return found

        # 2. Пробуем стандартные пути Linux
        linux_paths = ["/usr/local/bin/deno", "/usr/bin/deno", "/home/container/.deno/bin/deno"]
        for p in linux_paths:
            if os.path.exists(p):
                return p

        # 3. Пробуем стандартные пути Windows
        if os.name == 'nt':
            win_paths = [
                os.path.expandvars(r"%USERPROFILE%\.deno\bin\deno.exe"),
                r"C:\Program Files\deno\deno.exe"
            ]
            for p in win_paths:
                if os.path.exists(p):
                    return p

        return "deno"  # Fallback к PATH

    def check_deno(self):
        """Проверка доступности Deno и добавление в PATH"""
        try:
            # Пробуем запустить с текущим путем
            subprocess.run([self.deno_path, "--version"], capture_output=True, check=True)
            print(f"[OK] Deno found: {self.deno_path}")

            # Добавляем директорию Deno в системный PATH
            deno_dir = os.path.dirname(self.deno_path)
            if deno_dir and deno_dir not in os.environ.get('PATH', ''):
                os.environ['PATH'] = f"{deno_dir}{os.pathsep}{os.environ.get('PATH', '')}"
                print(f"[INFO] Deno directory added to PATH: {deno_dir}")

            return True
        except Exception:
            # Если не сработало, пробуем просто "deno"
            if self.deno_path != "deno":
                try:
                    subprocess.run(["deno", "--version"], capture_output=True, check=True)
                    self.deno_path = "deno"
                    print("[OK] Deno available via system PATH")
                    return True
                except Exception:
                    pass
            print("[WARN] Deno not found. Signature solving may not work.")
            return False

    def execute_ts(self, typescript_code, permissions=None):
        """Выполнение TypeScript кода"""
        if permissions is None:
            permissions = ["--allow-read"]

        with open("temp_exec.ts", "w") as f:
            f.write(typescript_code)

        try:
            cmd = [self.deno_path] + permissions + ["run", "temp_exec.ts"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Execution timeout",
                "returncode": 1
            }
        finally:
            if os.path.exists("temp_exec.ts"):
                os.remove("temp_exec.ts")

    def eval_ts(self, expression):
        """Быстрое вычисление выражения"""
        import json
        code = f"console.log(JSON.stringify({expression}))"
        result = self.execute_ts(code)
        if result["success"] and result["stdout"]:
            try:
                return json.loads(result["stdout"].strip())
            except:
                return result["stdout"].strip()
        return None


# Глобальный singleton
_deno_instance = None


def get_deno():
    """Возвращает singleton экземпляр DenoRuntime."""
    global _deno_instance
    if _deno_instance is None:
        _deno_instance = DenoRuntime()
    return _deno_instance
