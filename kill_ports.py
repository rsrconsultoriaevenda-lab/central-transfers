import subprocess
import os
import platform


def kill_process_on_port(port):
    """
    Encerra o processo que está escutando em uma porta específica.
    Compatível com Windows.
    """
    print(f"🔍 Verificando a porta {port}...")

    if platform.system() == "Windows":
        command = f"netstat -ano | findstr :{port}"
        try:
            output = subprocess.check_output(
                command, shell=True).decode('utf-8')
            lines = output.strip().split('\n')

            pids_found = set()
            for line in lines:
                if "LISTENING" in line:
                    parts = line.split()
                    if len(parts) > 4:
                        pid = parts[-1]
                        pids_found.add(pid)

            if pids_found:
                for pid in pids_found:
                    print(
                        f"  Processo com PID {pid} encontrado na porta {port}. Encerrando...")
                    try:
                        subprocess.run(
                            f"taskkill /PID {pid} /F", shell=True, check=True, capture_output=True)
                        print(f"  ✅ Processo {pid} encerrado com sucesso.")
                    except subprocess.CalledProcessError as e:
                        print(
                            f"  ❌ Erro ao encerrar PID {pid}: {e.stderr.decode('utf-8').strip()}")
            else:
                print(f"  Nenhum processo encontrado na porta {port}.")
        except subprocess.CalledProcessError:
            print(f"  Nenhum processo encontrado na porta {port}.")
        except Exception as e:
            print(f"  ❌ Erro inesperado ao verificar a porta {port}: {e}")
    else:
        print("Este script é otimizado para Windows. Para Linux/macOS, use 'lsof -i :PORT' e 'kill -9 PID'.")


if __name__ == "__main__":
    print("--- Limpando Portas de Desenvolvimento ---")
    kill_process_on_port(8001)  # Porta do Backend FastAPI
    kill_process_on_port(5173)  # Porta do Frontend (Vite)
    print("\n--- Verificação de Portas Concluída ---")
