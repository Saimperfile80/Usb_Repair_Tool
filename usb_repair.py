import usb.core
import usb.util
import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog
import logging

# Configuration du logging
logging.basicConfig(filename="usb_repair_tool.log", level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s")

def list_usb_devices_gui():
    """Lister les périphériques USB dans l'interface graphique."""
    try:
        devices = usb.core.find(find_all=True)
        if not devices:
            messagebox.showinfo("Information", "Aucun périphérique USB trouvé.")
            logging.warning("Aucun périphérique USB trouvé.")
            return []

        device_list = []
        for device in devices:
            device_info = f"ID: {hex(device.idVendor)}:{hex(device.idProduct)}"
            device_list.append(device_info)
        logging.info(f"{len(device_list)} périphériques USB trouvés.")
        return device_list
    except usb.core.USBError as e:
        messagebox.showerror("Erreur", f"Erreur lors de la recherche des périphériques USB : {e}")
        logging.error(f"Erreur lors de la recherche des périphériques USB : {e}")
        return []

def reset_usb_device_gui(device_id):
    """Réinitialiser un périphérique USB sélectionné via l'interface graphique."""
    try:
        device = usb.core.find(idVendor=device_id[0], idProduct=device_id[1])
        if device:
            device.reset()
            messagebox.showinfo("Succès", "Le périphérique USB a été réinitialisé avec succès.")
            logging.info(f"Périphérique {device_id} réinitialisé avec succès.")
        else:
            messagebox.showerror("Erreur", "Périphérique introuvable.")
            logging.warning(f"Périphérique {device_id} introuvable.")
    except usb.core.USBError as e:
        messagebox.showerror("Erreur", f"Erreur lors de la réinitialisation : {e}")
        logging.error(f"Erreur lors de la réinitialisation du périphérique {device_id}: {e}")

def analyze_and_repair_device_gui(device_path):
    """Analyser et réparer un périphérique USB via l'interface graphique."""
    try:
        subprocess.run(["sudo", "fsck", "-y", device_path], check=True)
        messagebox.showinfo("Succès", "Analyse et réparation terminées avec succès.")
        logging.info(f"Analyse et réparation du périphérique {device_path} terminées.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'analyse et de la réparation : {e}")
        logging.error(f"Erreur lors de l'analyse et de la réparation du périphérique {device_path}: {e}")

def format_usb_device_gui(device_path, filesystem="vfat"):
    """Formater un périphérique USB via l'interface graphique."""
    try:
        subprocess.run(["sudo", "mkfs", "-t", filesystem, device_path], check=True)
        messagebox.showinfo("Succès", "Formatage terminé avec succès.")
        logging.info(f"Périphérique {device_path} formaté avec le système de fichiers {filesystem}.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Erreur", f"Erreur lors du formatage : {e}")
        logging.error(f"Erreur lors du formatage du périphérique {device_path}: {e}")


# Interface principale
def main_gui():
    def list_devices():
        devices = list_usb_devices_gui()
        device_listbox.delete(0, tk.END)
        for device in devices:
            device_listbox.insert(tk.END, device)

    def reset_device():
        selected = device_listbox.curselection()
        if selected:
            device_info = device_listbox.get(selected)
            device_id = tuple(map(lambda x: int(x, 16), device_info.split(":")[1].split(".")))
            reset_usb_device_gui(device_id)
        else:
            messagebox.showwarning("Attention", "Veuillez sélectionner un périphérique.")

    def analyze_device():
        device_path = simpledialog.askstring("Chemin du périphérique", "Entrez le chemin du périphérique (ex: /dev/sdb1) :")
        if device_path:
            analyze_and_repair_device_gui(device_path)

    def format_device():
        device_path = simpledialog.askstring("Chemin du périphérique", "Entrez le chemin du périphérique (ex: /dev/sdb1) :")
        if device_path:
            filesystem = simpledialog.askstring("Système de fichiers", "Entrez le type de système de fichiers (vfat, ntfs, ext4) :")
            if filesystem:
                format_usb_device_gui(device_path, filesystem)

    root = tk.Tk()
    root.title("Outil de réparation USB")

    frame = tk.Frame(root)
    frame.pack(pady=10)

    list_button = tk.Button(frame, text="Lister les périphériques", command=list_devices)
    list_button.grid(row=0, column=0, padx=5)

    reset_button = tk.Button(frame, text="Réinitialiser", command=reset_device)
    reset_button.grid(row=0, column=1, padx=5)

    analyze_button = tk.Button(frame, text="Analyser et Réparer", command=analyze_device)
    analyze_button.grid(row=0, column=2, padx=5)

    format_button = tk.Button(frame, text="Formater", command=format_device)
    format_button.grid(row=0, column=3, padx=5)

    device_listbox = tk.Listbox(root, width=50)
    device_listbox.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main_gui()

