import usb.core
import usb.util
import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from tkinter import ttk

# Variables globales pour la langue
LANGUAGE = 'fr'  # Peut être 'fr' ou 'en'

def set_language(language):
    """Mettre à jour les textes de l'interface en fonction de la langue."""
    global LANGUAGE
    LANGUAGE = language

def translate(text):
    """Traduire le texte selon la langue sélectionnée."""
    translations = {
        'fr': {
            'list_devices': 'Lister les périphériques',
            'reset_device': 'Réinitialiser',
            'analyze_device': 'Analyser et Réparer',
            'format_device': 'Formater',
            'device_info': 'Informations du périphérique',
            'backup_data': 'Sauvegarder les données',
            'repair_bad_sectors': 'Réparer les secteurs défectueux',
            'choose_device': 'Veuillez sélectionner un périphérique.',
            'success': 'Succès',
            'error': 'Erreur',
            'warning': 'Attention',
            'usb_error': "Erreur lors de la réinitialisation : {e}",
            'no_device_found': 'Aucun périphérique USB trouvé.',
            'usb_reset_success': 'Le périphérique USB a été réinitialisé avec succès.',
            'usb_repair_success': 'Analyse et réparation terminées avec succès.',
            'usb_format_success': 'Formatage terminé avec succès.',
            'bad_sectors_repair_success': 'Réparation des secteurs défectueux terminée avec succès.',
            'backup_success': 'Les données ont été sauvegardées avec succès.',
        },
        'en': {
            'list_devices': 'List Devices',
            'reset_device': 'Reset Device',
            'analyze_device': 'Analyze and Repair',
            'format_device': 'Format',
            'device_info': 'Device Info',
            'backup_data': 'Backup Data',
            'repair_bad_sectors': 'Repair Bad Sectors',
            'choose_device': 'Please select a device.',
            'success': 'Success',
            'error': 'Error',
            'warning': 'Warning',
            'usb_error': "Error during reset: {e}",
            'no_device_found': 'No USB device found.',
            'usb_reset_success': 'USB device has been reset successfully.',
            'usb_repair_success': 'Analyze and repair completed successfully.',
            'usb_format_success': 'Formatting completed successfully.',
            'bad_sectors_repair_success': 'Bad sectors repair completed successfully.',
            'backup_success': 'Data has been backed up successfully.',
        }
    }
    return translations[LANGUAGE].get(text, text)

def list_usb_devices_gui():
    """Lister les périphériques USB dans l'interface graphique."""
    devices = usb.core.find(find_all=True)
    if not devices:
        messagebox.showinfo(translate('error'), translate('no_device_found'))
        return []

    device_list = []
    for device in devices:
        device_info = f"ID: {hex(device.idVendor)}:{hex(device.idProduct)}"
        device_list.append(device_info)
    return device_list

def reset_usb_device_gui(device_id):
    """Réinitialiser un périphérique USB sélectionné via l'interface graphique."""
    try:
        device = usb.core.find(idVendor=device_id[0], idProduct=device_id[1])
        if device:
            device.reset()
            messagebox.showinfo(translate('success'), translate('usb_reset_success'))
        else:
            messagebox.showerror(translate('error'), translate('usb_error').format(e='Device not found'))
    except usb.core.USBError as e:
        messagebox.showerror(translate('error'), translate('usb_error').format(e=e))

def analyze_and_repair_device_gui(device_path):
    """Analyser et réparer un périphérique USB via l'interface graphique."""
    try:
        subprocess.run(["sudo", "fsck", "-y", device_path], check=True)
        messagebox.showinfo(translate('success'), translate('usb_repair_success'))
    except subprocess.CalledProcessError as e:
        messagebox.showerror(translate('error'), f"Error during analysis and repair: {e}")

def format_usb_device_gui(device_path, filesystem="vfat"):
    """Formater un périphérique USB via l'interface graphique."""
    try:
        subprocess.run(["sudo", "mkfs", "-t", filesystem, device_path], check=True)
        messagebox.showinfo(translate('success'), translate('usb_format_success'))
    except subprocess.CalledProcessError as e:
        messagebox.showerror(translate('error'), f"Error during formatting: {e}")

def repair_bad_sectors(device_path):
    """Réparer les secteurs défectueux d'un périphérique USB."""
    try:
        subprocess.run(["sudo", "badblocks", "-v", device_path], check=True)
        messagebox.showinfo(translate('success'), translate('bad_sectors_repair_success'))
    except subprocess.CalledProcessError as e:
        messagebox.showerror(translate('error'), f"Error during bad sectors repair: {e}")

def backup_usb_data(device_path, backup_location):
    """Sauvegarder les données d'un périphérique USB."""
    try:
        subprocess.run(["rsync", "-av", device_path, backup_location], check=True)
        messagebox.showinfo(translate('success'), translate('backup_success'))
    except subprocess.CalledProcessError as e:
        messagebox.showerror(translate('error'), f"Error during backup: {e}")

def show_device_info(device_id):
    """Afficher les informations détaillées du périphérique USB."""
    device = usb.core.find(idVendor=device_id[0], idProduct=device_id[1])
    if device:
        device_info = f"Manufacturer: {usb.util.get_string(device, device.iManufacturer)}\n"
        device_info += f"Model: {usb.util.get_string(device, device.iProduct)}\n"
        device_info += f"Serial Number: {usb.util.get_string(device, device.iSerialNumber)}\n"
        messagebox.showinfo(translate('device_info'), device_info)
    else:
        messagebox.showerror(translate('error'), "Device not found.")

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
            messagebox.showwarning(translate('warning'), translate('choose_device'))

    def analyze_device():
        device_path = simpledialog.askstring(translate('analyze_device'), "Enter the device path (e.g., /dev/sdb1):")
        if device_path:
            analyze_and_repair_device_gui(device_path)

    def format_device():
        device_path = simpledialog.askstring(translate('format_device'), "Enter the device path (e.g., /dev/sdb1):")
        if device_path:
            filesystem = simpledialog.askstring(translate('format_device'), "Enter file system type (vfat, ntfs, ext4):")
            if filesystem:
                format_usb_device_gui(device_path, filesystem)

    def repair_sectors():
        device_path = simpledialog.askstring(translate('repair_bad_sectors'), "Enter the device path (e.g., /dev/sdb1):")
        if device_path:
            repair_bad_sectors(device_path)

    def backup_data():
        device_path = simpledialog.askstring(translate('backup_data'), "Enter the device path (e.g., /dev/sdb1):")
        if device_path:
            backup_location = filedialog.askdirectory(title="Choose Backup Location")
            if backup_location:
                backup_usb_data(device_path, backup_location)

    def show_info():
        selected = device_listbox.curselection()
        if selected:
            device_info = device_listbox.get(selected)
            device_id = tuple(map(lambda x: int(x, 16), device_info.split(":")[1].split(".")))
            show_device_info(device_id)
        else:
            messagebox.showwarning(translate('warning'), translate('choose_device'))

    root = tk.Tk()
    root.title("USB Repair Tool")

    frame = tk.Frame(root)
    frame.pack(pady=10)

    list_button = tk.Button(frame, text=translate('list_devices'), command=list_devices)
    list_button.grid(row=0, column=0, padx=5)

    reset_button = tk.Button(frame, text=translate('reset_device'), command=reset_device)
    reset_button.grid(row=0, column=1, padx=5)

    analyze_button = tk.Button(frame, text=translate('analyze_device'), command=analyze_device)
    analyze_button.grid(row=0, column=2, padx=5)

    format_button = tk.Button(frame, text=translate('format_device'), command=format_device)
    format_button.grid(row=0, column=3, padx=5)

    repair_button = tk.Button(frame, text=translate('repair_bad_sectors'), command=repair_sectors)
    repair_button.grid(row=1, column=0, padx=5)

    backup_button = tk.Button(frame, text=translate('backup_data'), command=backup_data)
    backup_button.grid(row=1, column=1, padx=5)

    info_button = tk.Button(frame, text=translate('device_info'), command=show_info)
    info_button.grid(row=1, column=2, padx=5)

    device_listbox = tk.Listbox(root, width=60, height=10)
    device_listbox.pack(pady=10)

    root.mainloop()

# Exécution du programme
if __name__ == "__main__":
    main_gui()

