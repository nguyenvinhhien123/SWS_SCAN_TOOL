import subprocess
import os
import datetime
import sys
import requests
import json
import random
import time

# --- COLOR CONFIG ---
R = '\033[31m'; G = '\033[32m'; Y = '\033[33m'; B = '\033[34m'
W = '\033[37m'; C = '\033[0m' 

XSSTRIKE_PATH = "/home/kali/swit-scanner/apps/XSStrike/xsstrike.py"
CURRENT_PROXY = ""
CURRENT_LOG_FILE = ""

# ---------------- UI ----------------

def banner():
    os.system('clear')
    print(f"{B}")
    print(r"    ███████╗██╗    ██╗███████╗")
    print(r"    ██╔════╝██║    ██║██╔════╝")
    print(r"    ███████╗██║ █╗ ██║███████╗")
    print(r"    ╚════██║██║███╗██║╚════██║")
    print(r"    ███████║╚███╔███╔╝███████║")
    print(r"    ╚══════╝ ╚══╝╚══╝ ╚══════╝")
    print(f"{Y} ╔" + "═"*60 + "╗")
    p_status = f"{G}{CURRENT_PROXY}{C}" if CURRENT_PROXY else f"{R}DIRECT (ALIVE){C}"
    print(f" ║  ILOVEYOURWEB Version 1.1  ║ PROXY: {p_status}")
    print(f"{Y} ╚" + "═"*60 + "╝")

# ---------------- PROXY ----------------

def set_proxy(proxy_str):
    global CURRENT_PROXY
    proxy_str = proxy_str.strip().replace('\r', '')
    formatted_p = proxy_str if proxy_str.startswith("http") else f"http://{proxy_str}"
    print(f"\n{Y}[*] Validating Proxy: {formatted_p}...{C}")
    try:
        requests.get("http://www.google.com",
                     proxies={"http": formatted_p, "https": formatted_p},
                     timeout=7)
        CURRENT_PROXY = formatted_p
        print(f"{G}[✔] Proxy is ALIVE!{C}")
        return True
    except:
        print(f"{R}[!] Proxy is DEAD or Timeout.{C}")
        return False

# ---------------- LOG ----------------

def init_log(target, tool_name="general"):
    global CURRENT_LOG_FILE
    clean_name = target.replace("http://", "").replace("https://", "") \
                       .replace("/", "_").replace("#", "").split('?')[0]
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    tool_name = tool_name.lower().replace(" ", "_")
    CURRENT_LOG_FILE = f"scan_{tool_name}_{clean_name}_{ts}.log"

    with open(CURRENT_LOG_FILE, "w") as f:
        f.write(f"=== TOOL: {tool_name.upper()} ===\n")
        f.write(f"=== TARGET: {target} ===\n")
        f.write(f"=== TIMESTAMP: {datetime.datetime.now()} ===\n\n")

    print(f"{G}[!] Session Log Initialized: {CURRENT_LOG_FILE}{C}")

def run_command(command, description):
    print(f"\n{G}[+] {description}...{C}")
    if not CURRENT_LOG_FILE:
        return

    env = os.environ.copy()
    if CURRENT_PROXY:
        env["http_proxy"] = env["https_proxy"] = env["HTTP_PROXY"] = env["HTTPS_PROXY"] = CURRENT_PROXY
    
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env
        )
        for line in process.stdout:
            print(line, end='')
            with open(CURRENT_LOG_FILE, "a") as f:
                f.write(line)
        process.wait()
    except Exception as e:
        print(f"{R}[!] Error executing {description}: {e}{C}")

def get_formatted_logs():
    logs = [f for f in os.listdir('.') if f.startswith("scan_") and f.endswith('.log')]
    formatted_list = []

    for f in logs:
        try:
            mtime = os.path.getmtime(f)
            dt_obj = datetime.datetime.fromtimestamp(mtime)
            readable_time = dt_obj.strftime("%b %d, %Y - %H:%M:%S")
            formatted_list.append((f, readable_time, mtime))
        except:
            formatted_list.append((f, "Unknown Date", 0))

    formatted_list.sort(key=lambda x: x[2], reverse=True)
    return [(f, t) for f, t, _ in formatted_list]

# ---------------- AI LOG ANALYSIS (NEW) ----------------

def _select_log_file():
    logs = get_formatted_logs()
    if not logs:
        print(f"{R}[!] No scan logs found in current directory.{C}")
        return None

    print(f"\n{G}Scan History:{C}")
    for i, (fname, ftime) in enumerate(logs):
        print(f" [{i}] {ftime} -> {W}{fname}{C}")

    l_idx = input(f"{Y}\nEnter log index: {C}")
    if not l_idx.isdigit() or int(l_idx) >= len(logs):
        print(f"{R}[!] Invalid index.{C}")
        return None
    return logs[int(l_idx)][0]

def _build_log_analysis_prompt(log_text, log_filename):
    # Keep this prompt detailed + professional; user can paste into ChatGPT or any LLM.
    return f"""Bạn là một chuyên gia Security Analyst/Pentester. Hãy phân tích **file log scan** dưới đây một cách chi tiết, chuyên nghiệp và có cấu trúc.

## 1) Mục tiêu
- Tóm tắt những gì tool đã làm và bối cảnh scan (tool, target, thời gian, proxy nếu có).
- Trích xuất các phát hiện quan trọng (dịch vụ/port, endpoint, lỗi, dấu hiệu vuln, CVE, payload, response đáng chú ý).
- Đánh giá mức độ rủi ro (Critical/High/Medium/Low/Info) theo logic thực tế, nêu rõ lý do.
- Đề xuất bước tiếp theo (manual verification, exploitability check, hardening, retest plan).
- Nếu log có lỗi/timeout/false positive: chỉ ra vị trí và gợi ý cách chạy lại (tham số, proxy, timeout, scope).

## 2) Yêu cầu đầu ra (format bắt buộc)
### A. Executive Summary (5-10 dòng)
- Target, phạm vi, kết quả tổng quan.
### B. Kết quả theo từng module/tool
- Nmap: ports/services/versions, nhận xét fingerprint.
- Katana/Crawl: endpoints quan trọng, tham số, auth boundary, phát hiện bề mặt tấn công.
- XSStrike/XSS: tham số nghi ngờ, vector, mức tin cậy, hướng verify thủ công.
- Nuclei/CVE/Tech: template match, bằng chứng trong log, cảnh báo false positive.
- SQLMap/SQLi: tham số, kiểu injection, bằng chứng, mức độ khai thác.
*(Nếu log chỉ có 1-2 module thì chỉ viết phần tương ứng.)*
### C. Dòng log quan trọng (trích dẫn)
- Liệt kê 10-30 dòng log quan trọng nhất (nguyên văn) + giải thích vì sao quan trọng.
### D. Danh sách Issues (bảng)
- Issue | Evidence (log line) | Impact | Likelihood | Severity | Recommendation | Verification steps
### E. Kế hoạch hành động
- Quick wins (1-2 ngày)
- Hardening (1-2 tuần)
- Retest checklist

## 3) Lưu ý
- Không bịa dữ liệu: mọi kết luận phải bám vào evidence trong log.
- Nếu thiếu evidence, hãy ghi rõ “Không đủ dữ liệu trong log”.

## 4) LOG INPUT
- File: {log_filename}

```log
{log_text}
```
"""

def _truncate_log_for_llm(log_text, max_chars=20000):
    """Keep logs within a practical size for LLM context.
    Uses head+tail strategy with a clear truncation marker.
    """
    try:
        max_chars = int(max_chars)
    except:
        max_chars = 20000

    if max_chars <= 0:
        return log_text

    if len(log_text) <= max_chars:
        return log_text

    # Keep ~60% head, ~40% tail for better context.
    head_len = int(max_chars * 0.6)
    tail_len = max_chars - head_len
    head = log_text[:head_len]
    tail = log_text[-tail_len:]
    marker = "\n\n--- [TRUNCATED: log too large, showing head+tail only] ---\n\n"
    return head + marker + tail

def ai_log_analysis_prompt_generator():
    log_file = _select_log_file()
    if not log_file:
        input("\nPress Enter to return...")
        return

    try:
        with open(log_file, "r", errors="ignore") as f:
            log_text = f.read()
    except Exception as e:
        print(f"{R}[!] Failed to read log: {e}{C}")
        input("\nPress Enter to return...")
        return

    # Build the professional analysis prompt (we'll both SAVE it and (optionally) RUN it).
    prompt_max = os.getenv("PROMPT_LOG_MAX_CHARS", "60000")
    log_for_prompt = _truncate_log_for_llm(log_text, max_chars=prompt_max)
    prompt = _build_log_analysis_prompt(log_for_prompt, log_file)

    # Always export the prompt for traceability/reuse.
    out_name = f"scan_ai_prompt_{os.path.basename(log_file).replace('.log','')}.log"
    try:
        with open(out_name, "w") as f:
            f.write(prompt)
        print(f"\n{G}[✔] Prompt saved to: {W}{out_name}{C}")
    except Exception as e:
        print(f"{R}[!] Failed to save prompt file: {e}{C}")

    # If API key is available, run AI analysis immediately using the prompt.
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if api_key:
        print(f"\n{G}[+] Running AI log analysis using saved prompt...{C}")

        # Use a clear system role, but keep the bulk of instructions in user prompt.
        system_prompt = (
            "You are a senior Security Analyst/Pentester. "
            "Follow the user's prompt precisely. "
            "Do not invent evidence; cite short snippets from the log when making claims."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        ans = _openai_chat(messages, temperature=0.2)
        if ans:
            report_name = f"ai_report_{os.path.basename(log_file)}.md"
            try:
                with open(report_name, "w") as f:
                    f.write(f"# AI Log Analysis Report\n\n")
                    f.write(f"**Log file:** `{log_file}`\n\n")
                    f.write(f"**Prompt file:** `{out_name}`\n\n")
                    f.write(ans)
                print(f"\n{G}[✔] AI report saved to: {W}{report_name}{C}")
            except Exception as e:
                print(f"{R}[!] Failed to save AI report: {e}{C}")

            print(f"\n{Y}--- AI ANALYSIS OUTPUT ---{C}\n")
            print(ans)
        else:
            print(f"{R}[!] AI analysis failed (API error above).{C}")
            print(f"{Y}You can still copy the saved prompt into ChatGPT/LLM manually: {W}{out_name}{C}")
    else:
        print(f"\n{Y}[!] OPENAI_API_KEY not found. Option 7 can auto-analyze only if you set the key BEFORE running.{C}")
        script = os.path.basename(sys.argv[0]) if sys.argv else "ILOVEYOURWEB.py"
        print(f"{W}Linux/macOS:{C}  export OPENAI_API_KEY='YOUR_KEY'  &&  python {script}")
        print(f"{W}PowerShell:{C}   setx OPENAI_API_KEY 'YOUR_KEY'  (reopen terminal)  ;  python {script}")
        print(f"\n{Y}--- COPY THIS PROMPT INTO CHATGPT/LLM ---{C}\n")
        print(prompt)

    input("\nPress Enter to return...")

def _openai_chat(messages, model=None, temperature=0.2):
    # Minimal OpenAI REST call via environment variable OPENAI_API_KEY.
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print(f"{R}[!] OPENAI_API_KEY not found in environment.{C}")
        print(f"{Y}Set it BEFORE running the tool, then run again:{C}")
        script = os.path.basename(sys.argv[0]) if sys.argv else "ILOVEYOURWEB.py"
        print(f"{W}Linux/macOS:{C}  export OPENAI_API_KEY='YOUR_KEY'  &&  python {script}")
        print(f"{W}PowerShell:{C}   setx OPENAI_API_KEY 'YOUR_KEY'  (reopen terminal)  ;  python {script}")
        return None

    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    try:
        r = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": model,
                "messages": messages,
                "temperature": temperature
            }),
            timeout=60
        )
        if r.status_code != 200:
            print(f"{R}[!] OpenAI API error {r.status_code}:{C} {r.text[:500]}")
            return None
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"{R}[!] OpenAI request failed: {e}{C}")
        return None

def ai_chat_with_log():
    # Chat mode uses OpenAI API. Key MUST be provided via environment variable.
    # (We do NOT store keys in code.)
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print(f"{R}[!] OPENAI_API_KEY not found in environment.{C}")
        print(f"{Y}Set it BEFORE running the tool, then run the tool again.{C}")
        script = os.path.basename(sys.argv[0]) if sys.argv else "ILOVEYOURWEB.py"
        print(f"{W}Linux/macOS:{C}  export OPENAI_API_KEY='YOUR_KEY'  &&  python {script}")
        print(f"{W}PowerShell:{C}   setx OPENAI_API_KEY 'YOUR_KEY'  (reopen terminal)  ;  python {script}")
        input("\nPress Enter to return...")
        return

    log_file = _select_log_file()
    if not log_file:
        input("\nPress Enter to return...")
        return

    try:
        with open(log_file, "r", errors="ignore") as f:
            log_text = f.read()
    except Exception as e:
        print(f"{R}[!] Failed to read log: {e}{C}")
        input("\nPress Enter to return...")
        return

    system_prompt = (
        "You are a professional pentest log analyst. "
        "Answer questions based ONLY on the provided log content. "
        "When you make claims, cite short evidence snippets from the log. "
        "If the log does not contain enough info, say so and suggest what to collect next."
    )

    # Keep chat context bounded to avoid token overflow.
    chat_max = os.getenv("CHAT_LOG_MAX_CHARS", "20000")
    log_for_chat = _truncate_log_for_llm(log_text, max_chars=chat_max)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Here is the scan log file ({log_file}). Use it as context for all answers.\n\n```log\n{log_for_chat}\n```"}
    ]

    print(f"\n{G}[AI CHAT MODE]{C} Linked log: {W}{log_file}{C}")
    print(f"{Y}Type your question. Commands: /exit, /save, /model <name>, /temp <0-1>{C}\n")

    temperature = 0.2

    while True:
        q = input(f"{B}You>{C} ").strip()
        if not q:
            continue
        if q.lower() in ["/exit", "exit", "quit", "/quit"]:
            break

        if q.startswith("/model"):
            parts = q.split(maxsplit=1)
            if len(parts) == 2 and parts[1].strip():
                os.environ["OPENAI_MODEL"] = parts[1].strip()
                print(f"{G}[✔] Model set to: {W}{os.environ['OPENAI_MODEL']}{C}")
            else:
                print(f"{R}[!] Usage: /model <model_name>{C}")
            continue

        if q.startswith("/temp"):
            parts = q.split(maxsplit=1)
            try:
                t = float(parts[1].strip())
                if 0 <= t <= 1:
                    temperature = t
                    print(f"{G}[✔] Temperature set to: {W}{temperature}{C}")
                else:
                    print(f"{R}[!] Temperature must be between 0 and 1.{C}")
            except:
                print(f"{R}[!] Usage: /temp <0-1>{C}")
            continue

        if q.lower() == "/save":
            out_name = f"chat_{os.path.basename(log_file)}.md"
            try:
                with open(out_name, "w") as f:
                    for m in messages:
                        f.write(f"### {m['role'].upper()}\n\n{m['content']}\n\n")
                print(f"{G}[✔] Chat saved to: {W}{out_name}{C}")
            except Exception as e:
                print(f"{R}[!] Failed to save chat: {e}{C}")
            continue

        messages.append({"role": "user", "content": q})
        ans = _openai_chat(messages, temperature=temperature)
        if not ans:
            # API error already printed.
            continue

        messages.append({"role": "assistant", "content": ans})
        print(f"\n{G}AI>{C} {ans}\n")

    input("\nPress Enter to return...")


# ---------------- SECURITY TOOLS ----------------

def nmap_scan(target):
    domain = target.replace("http://", "").replace("https://", "").split('/')[0].split('#')[0]
    run_command(f"nmap -F -sV -Pn {domain}", "Nmap Infrastructure Scanning")

def katana_crawl(target):
    cmd = f"katana -u {target} -headless -jc -d 2"
    if CURRENT_PROXY:
        cmd += f" -proxy {CURRENT_PROXY}"
    run_command(cmd, "Katana Headless Crawling")

def xsstrike_scan(target):
    if os.path.exists(XSSTRIKE_PATH):
        clean_url = target.split('#')[0]
        cmd = f"python3 {XSSTRIKE_PATH} -u \"{clean_url}\" --crawl --timeout 15"
        if CURRENT_PROXY:
            cmd += " --proxy"
        run_command(cmd, "XSStrike Vulnerability Scan")

def cve_scan(target):
    cmd = f"nuclei -u {target} -as -severity low,medium,high,critical"
    if CURRENT_PROXY:
        cmd += f" -proxy {CURRENT_PROXY}"
    run_command(cmd, "Nuclei Advanced CVE & Tech Scan")

def sql_scan(target):
    cmd = f"sqlmap -u \"{target}\" --crawl=2 --forms --batch --threads=3 --level=2 --risk=1"
    if CURRENT_PROXY:
        cmd += f" --proxy=\"{CURRENT_PROXY}\""
    run_command(cmd, "SQLMap Automated Injection Scan")

# ---------------- MAIN MENU ----------------

def main_menu():
    global CURRENT_PROXY, CURRENT_LOG_FILE
    while True:
        banner()
        print(f" 1.  {G}Full Audit {C}")
        print(f" 2.  Nmap Scan")
        print(f" 3.  Web Crawl")
        print(f" 4.  XSS Vulne Scan")
        print(f" 5.  Advanced CVE Scan")
        print(f" 6.  SQLMap Scan")
        print(f" 7.  {G}AI Log Analysis Prompt (from Scan Log){C}")
        print(f" 8.  {G}Log File {C}")
        print(f" 9.  {G}Fetch Proxy from Scrape API {C}")
        print(f" 10. {G}Load Proxy File {C}")
        print(f" 11. Exit")
        print(f" 12. {G}Chat with AI (linked to Scan Log){C}")
        
        choice = input(f"{Y}\nSelect Option: {C}")

        if choice == '11':
            break

        # -------- VIEW LOG --------
        elif choice == '8':
            logs = get_formatted_logs()
            if not logs:
                print(f"{R}[!] No scan logs found in current directory.{C}")
            else:
                print(f"\n{G}Scan History:{C}")
                for i, (fname, ftime) in enumerate(logs):
                    print(f" [{i}] {ftime} -> {W}{fname}{C}")
                
                l_idx = input(f"{Y}\nEnter index to view log: {C}")
                if l_idx.isdigit() and int(l_idx) < len(logs):
                    os.system(f"less -R {logs[int(l_idx)][0]}")
            input("\nPress Enter to return...")
            continue

        # -------- AI LOG PROMPT GENERATOR --------
        elif choice == '7':
            ai_log_analysis_prompt_generator()
            continue

        # -------- AI CHAT WITH LOG --------
        elif choice == '12':
            ai_chat_with_log()
            continue

        # -------- PROXY --------
        elif choice == '9':
            try:
                res = requests.get(
                    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http",
                    timeout=10
                )
                set_proxy(res.text.strip().split('\r\n')[0])
            except:
                print(f"{R}[!] Failed to fetch API proxy.{C}")
            input("\nPress Enter...")
            continue

        elif choice == '10':
            files = [f for f in os.listdir('.') if f.endswith('.txt')]
            if not files:
                print(f"{R}[!] No .txt files found.{C}")
            else:
                for i, f in enumerate(files):
                    print(f" [{i}] {f}")
                f_idx = input(f"{Y}Select file index: {C}")
                if f_idx.isdigit() and int(f_idx) < len(files):
                    with open(files[int(f_idx)], 'r') as f:
                        proxies = [l.strip() for l in f if l.strip()]
                        if proxies:
                            set_proxy(random.choice(proxies))
            input("\nPress Enter...")
            continue

        # -------- TARGET INPUT --------
        target = input(f"{Y}Target URL (e.g., http://example.com): {C}").strip()
        if not target.startswith("http"):
            print(f"{R}[!] Error: Target must include http:// or https://{C}")
            time.sleep(1.5)
            continue

        # -------- INIT LOG BASED ON TOOL --------
        if choice == '1':
            init_log(target, "full")
            nmap_scan(target)
            katana_crawl(target)
            xsstrike_scan(target)
            cve_scan(target)
            sql_scan(target)

        elif choice == '2':
            init_log(target, "nmap")
            nmap_scan(target)

        elif choice == '3':
            init_log(target, "katana")
            katana_crawl(target)

        elif choice == '4':
            init_log(target, "xsstrike")
            xsstrike_scan(target)

        elif choice == '5':
            init_log(target, "nuclei")
            cve_scan(target)

        elif choice == '6':
            init_log(target, "sqlmap")
            sql_scan(target)

        input(f"\n{G}>>> Scan Completed. Log saved. Press Enter to return...{C}")

if __name__ == "__main__":
    main_menu()
