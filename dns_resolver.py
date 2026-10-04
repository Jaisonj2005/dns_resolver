import tkinter as tk
from tkinter import ttk, messagebox
import socket
import threading

# Global flag for stopping the thread gracefully
is_resolving = False

def start_resolution():
    global is_resolving
    
    # Get text from input and clean it up
    raw_text = text_input.get(1.0, tk.END).strip()
    if not raw_text:
        messagebox.showerror("Input Error", "Please enter at least one domain to resolve.")
        return

    # Split by newline and remove empty lines
    domains = [d.strip() for d in raw_text.split('\n') if d.strip()]
    
    is_resolving = True
    btn_start.config(state=tk.DISABLED)
    btn_stop.config(state=tk.NORMAL)
    
    text_output.config(state=tk.NORMAL)
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, f"[*] Starting Bulk DNS Resolution for {len(domains)} targets...\n")
    text_output.insert(tk.END, "-" * 55 + "\n")
    text_output.config(state=tk.DISABLED)
    
    lbl_status.config(text="Resolving domains...", fg="#e67e22")
    
    # Offload network requests to background thread
    threading.Thread(target=resolve_domains, args=(domains,), daemon=True).start()

def resolve_domains(domains):
    global is_resolving
    success_count = 0
    
    for domain in domains:
        if not is_resolving:
            insert_log("\n[!] Resolution aborted by user.")
            break
            
        try:
            # Strip http/https if the user accidentally pasted full URLs
            clean_domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
            
            # Perform DNS A-Record lookup
            ip_address = socket.gethostbyname(clean_domain)
            
            insert_log(f"[+] {clean_domain:<25} -> {ip_address}\n", tag="success")
            success_count += 1
            
        except socket.gaierror:
            # NXDOMAIN (Non-Existent Domain) or network drop
            insert_log(f"[-] {clean_domain:<25} -> NXDOMAIN (Unresolved)\n", tag="error")
        except Exception as e:
            insert_log(f"[!] {clean_domain:<25} -> Error: {str(e)}\n", tag="error")
            
        # Update UI label for progress
        lbl_status.after(0, lambda d=clean_domain: lbl_status.config(text=f"Querying: {d}"))
        
    insert_log("-" * 55 + f"\n[*] Complete. Resolved {success_count} out of {len(domains)} domains.\n")
    root.after(0, reset_ui)

def insert_log(message, tag=None):
    text_output.config(state=tk.NORMAL)
    text_output.insert(tk.END, message, tag)
    text_output.see(tk.END)
    text_output.config(state=tk.DISABLED)

def stop_resolution():
    global is_resolving
    is_resolving = False
    lbl_status.config(text="Stopping...", fg="#c0392b")

def reset_ui():
    btn_start.config(state=tk.NORMAL)
    btn_stop.config(state=tk.DISABLED)
    lbl_status.config(text="Ready", fg="#7f8c8d")

# --- Tkinter GUI Layout ---
root = tk.Tk()
root.title("SOC Toolkit - Bulk DNS Resolver")
root.geometry("750x550")
root.resizable(False, False)

frame = ttk.Frame(root, padding="15")
frame.pack(fill=tk.BOTH, expand=True)

lbl_title = tk.Label(frame, text="Bulk DNS & Subdomain Resolver", font=("Helvetica", 13, "bold"))
lbl_title.pack(anchor="w", pady=(0, 10))

# PanedWindow for split view
paned_window = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
paned_window.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

# Left Pane: Input
frame_left = ttk.Frame(paned_window)
paned_window.add(frame_left, weight=1)

tk.Label(frame_left, text="Paste Domains (One per line):", font=("Helvetica", 9, "bold")).pack(anchor="w")
text_input = tk.Text(frame_left, font=("Consolas", 10), width=30)
text_input.pack(fill=tk.BOTH, expand=True, pady=5)
text_input.insert(tk.END, "google.com\ncisco.com\nsystech.in\nmalicious-fake-site.xyz\ngithub.com")

# Right Pane: Output
frame_right = ttk.Frame(paned_window)
paned_window.add(frame_right, weight=2)

tk.Label(frame_right, text="Resolution Results:", font=("Helvetica", 9, "bold")).pack(anchor="w")
scrollbar = tk.Scrollbar(frame_right)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text_output = tk.Text(frame_right, font=("Consolas", 10), bg="#1e1e1e", fg="#ecf0f1", yscrollcommand=scrollbar.set)
text_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5)
text_output.tag_config("success", foreground="#2ecc71")
text_output.tag_config("error", foreground="#e74c3c")
text_output.config(state=tk.DISABLED)
scrollbar.config(command=text_output.yview)

# Controls
control_frame = tk.Frame(frame)
control_frame.pack(fill=tk.X)

btn_start = tk.Button(control_frame, text="Resolve Targets", command=start_resolution, bg="#2980b9", fg="white", font=("Helvetica", 9, "bold"), width=15)
btn_start.pack(side=tk.LEFT, padx=(0, 10))

btn_stop = tk.Button(control_frame, text="Stop", command=stop_resolution, bg="#c0392b", fg="white", font=("Helvetica", 9, "bold"), width=10, state=tk.DISABLED)
btn_stop.pack(side=tk.LEFT)

lbl_status = tk.Label(control_frame, text="Ready", font=("Consolas", 9), fg="#7f8c8d")
lbl_status.pack(side=tk.RIGHT)

root.mainloop()