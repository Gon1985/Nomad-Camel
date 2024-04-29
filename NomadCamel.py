import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser, font
import json
import os
from PIL import Image, ImageTk
import pygame
import threading
import time
from datetime import datetime
import math


class ResizableTextBox:
    def __init__(self, master):
        self.master = master
        self.master.title("Resizable Text Box")
        self.master.geometry("600x300")

        self.text_box = tk.Text(self.master, wrap="word", height=5, width=30)
        self.text_box.pack(padx=10, pady=10, expand=True, fill="both")

        
        self.size_selector = tk.Scale(self.master, from_=5, to=50, orient="horizontal", label="Size")
        self.size_selector.set(15)  
        self.size_selector.pack(pady=10)
        
        #
        self.open_button = tk.Button(self.master, text="Open Text Box", command=self.open_text_box)
        self.open_button.pack(pady=10)
        
        
        self.text = tk.Text(self.master, wrap="word", bg=self.bg_color, font=(self.current_font, self.font_size))
        self.text.pack(expand=True, fill="both")
        self.update_font_info_panel()
        
        
        
    def open_text_box(self):
        text_box_window = tk.Toplevel(self.master)
        text_box_window.title("Resizable Text Box")

        
        text_box = tk.Text(text_box_window, wrap="word", height=5, width=30, font=("Arial", self.size_selector.get()))
        text_box.pack(padx=10, pady=10, expand=True, fill="both")

        
        def update_text_box_size(value):
            text_box.config(font=("Arial", int(value)))

        self.size_selector.config(command=update_text_box_size)



class NotepadApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Nomad Camel")
        self.master.geometry("800x700")
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)  
        
        
        self.about_window = None  
        self.help_window = None
        
        
        pygame.mixer.init()

        
        intro_sound_path = "sounds/introsound.mp3"  
        if os.path.exists(intro_sound_path):
            pygame.mixer.music.load(intro_sound_path)
            pygame.mixer.music.play()
        else:
            print("El archivo de sonido no se encontró.")
            
        
        about_sound_path = "sounds/about.mp3"
        if os.path.exists(about_sound_path):
            self.about_sound = pygame.mixer.Sound(about_sound_path)
        else:
            print("El archivo de sonido para la ventana 'About' no se encontró.")    
            
            
        self.close_sound = None
        close_sound_path = "sounds/exit.mp3"
        if os.path.exists(close_sound_path):
            self.close_sound = pygame.mixer.Sound(close_sound_path)
        else:
            print("El archivo de sonido de cierre no se encontró.")
            
            
        self.save_sound_path = "sounds/exit.mp3"  
        if os.path.exists(self.save_sound_path):
            self.save_sound = pygame.mixer.Sound(self.save_sound_path)
        else:
            print("El archivo de sonido de guardado no se encontró.")    
            
            
        
        self.bg_color = "#e7c22b"
        self.master.configure(bg=self.bg_color)
        
        
        icon_path = "images/camelicon.ico" 
        if os.path.exists(icon_path):
            self.master.iconbitmap(icon_path)

        self.font_size = 12  
        self.current_font = "Helvetica"  
        self.text = tk.Text(self.master, wrap="word", bg=self.bg_color, font=(self.current_font, self.font_size))
        
        self.text.grid(row=1, column=0, sticky='nsew')
        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        
        self.create_font_info_panel()
        self.update_font_info_label() 
        self.update_clock_and_date()  
        

        self.menu_bar = tk.Menu(self.master)
        self.master.config(menu=self.menu_bar)

        
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Create File", command=self.confirm_create_file)
        self.file_menu.add_command(label="Open File", command=self.open_file)
        self.file_menu.add_command(label="Save File", command=self.save_file_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Close program", command=self.on_closing)

        
        self.config_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Configuration", menu=self.config_menu)
        self.config_menu.add_command(label="Change Background Color", command=self.change_bg_color)
        self.config_menu.add_command(label="Change Text Color", command=self.change_text_color)
        self.config_menu.add_command(label="Change Font", command=self.change_font)
        self.config_menu.add_command(label="Change Font Size", command=self.change_font_size)
        self.config_menu.add_separator()
        self.config_menu.add_command(label="Save Configuration", command=self.save_configuration)
        self.config_menu.add_command(label="Load Configuration", command=self.load_configuration)
        self.config_menu.add_command(label="Restore Default Configuration", command=self.restore_default_configuration)
        
        
        self.encryption_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Encryption", menu=self.encryption_menu)
        self.encryption_menu.add_command(label="Encrypt Text", command=self.encrypt_text)
        self.encryption_menu.add_command(label="Decrypt Text", command=self.decrypt_text)
        
        
        self.current_file = None
        self.config_file_path = "config.json"
        self.create_context_menu()
        
    
    
    
    def create_context_menu(self):
        self.context_menu = tk.Menu(self.master, tearoff=0)
        self.context_menu.add_command(label="About", command=self.show_about)
        self.context_menu.add_command(label="Help", command=self.show_help_window)  
        

        
        self.master.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()



    def create_font_info_panel(self):
        font_info_frame = tk.Frame(self.master, bg=self.bg_color)
        font_info_frame.grid(row=0, column=0, sticky='ew')

        self.font_info_label = tk.Label(font_info_frame, bg=self.bg_color, fg='black', padx=5, pady=5)
        self.font_info_label.pack(side='left')
        self.update_font_info_label()

        self.clock_date_label = tk.Label(font_info_frame, bg=self.bg_color, fg='black', padx=5, pady=5)
        self.clock_date_label.pack(side='left')

    def update_font_info_label(self):
        self.font_info_label.config(text=f"Font: {self.current_font} | Size: {self.font_size}")

    def update_clock_and_date(self):
        current_time = time.strftime("%H:%M:%S")  
        current_date = datetime.now().strftime("%A, %B %d, %Y")  
        self.clock_date_label.config(text=f"{current_time} | {current_date}")
        self.clock_date_label.after(1000, self.update_clock_and_date)  
        
    

    def show_about(self):
        if self.about_window and self.about_window.winfo_exists():
            self.about_window.focus()
            return

        self.about_window = tk.Toplevel(self.master)
        self.about_window.title("About Nomad Camel")
        self.about_window.resizable(False, False)

        
        icon_path = "images/camelicon.ico"
        if os.path.exists(icon_path):
            self.about_window.iconbitmap(icon_path)

    
        if hasattr(self, 'about_sound'):
            self.about_sound.play()


        image_path = "images/about.png"
        if os.path.exists(image_path):
            img = Image.open(image_path)
            photo = ImageTk.PhotoImage(img)
            
            self.about_window.geometry(f"{img.width}x{img.height}")
            img_label = tk.Label(self.about_window, image=photo, borderwidth=0)
            img_label.image = photo  
            img_label.pack(fill='both', expand=True)
        else:
            tk.Label(self.about_window, text="Image not found!").pack(pady=20)

        
        self.about_window.protocol("WM_DELETE_WINDOW", self.close_about_window)

    def close_about_window(self):
        self.about_window.destroy()
        self.about_window = None
    
    
    
    
    
    def show_help_window(self):
        if self.help_window and self.help_window.winfo_exists():
            return

        self.help_window = tk.Toplevel(self.master)
        self.help_window.title("Help")
        self.help_window.geometry("650x300")
        self.help_window.configure(bg="#e7c22b")
        self.help_window.resizable(False, False)
        
        
        icon_path = "images/camelicon.ico"
        if os.path.exists(icon_path):
            self.help_window.iconbitmap(icon_path)
        
        
        help_text = """
        Welcome to the Nomad Camel help section.
        ***************************************************
        
        1) Start working on your text, define the size and type of font in the configuration section.
        When you select change font, you will see the fonts installed on your system reflected.
        
        2) You can change the background color and text color in the configuration section once again.
        
        3) If you want to save the configuration, click on save configuration and define a name for your workspace.
        Here the chosen color will be saved along with the chosen font.
        
        4) Don't forget to save your text in the File section.
        
        """

        
        help_label = tk.Label(self.help_window, text=help_text, bg="#e7c22b", justify="center", padx=20, pady=20)
        help_label.pack(expand=True, fill="both")

        
        self.help_window.protocol("WM_DELETE_WINDOW", self.close_help_window)

    def close_help_window(self):
        if self.help_window is not None:
            self.help_window.destroy()
            self.help_window = None


        
    def change_font(self):
        if hasattr(self, 'font_window') and self.font_window is not None and not self.font_window.winfo_destroyed():
            self.font_window.focus()
            return

    
        self.font_window = tk.Toplevel(self.master)
        self.font_window.title("Choose Font")
        self.font_window.geometry("250x300")
        self.font_window.configure(bg="#e7c22b")
        
        
        icon_path = "images/camelicon.ico"  
        if os.path.exists(icon_path):
            self.font_window.iconbitmap(icon_path)
        

        
        self.font_window.protocol("WM_DELETE_WINDOW", self.on_font_window_close)

        
        search_var = tk.StringVar()
        search_entry = tk.Entry(self.font_window, textvariable=search_var)
        search_entry.pack(fill="x", padx=5, pady=5)

        scrollbar = tk.Scrollbar(self.font_window)
        scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(self.font_window, yscrollcommand=scrollbar.set, exportselection=False, bg="#e7c22b")
        fonts = list(tk.font.families())
        fonts.sort()

        
        def update_list():
            search_term = search_var.get()
            listbox.delete(0, tk.END)
            for font in fonts:
                if search_term.lower() in font.lower():
                    listbox.insert(tk.END, font)

        
        search_button = tk.Button(self.font_window, text="Search", command=update_list, bg="#d9d8d7")  
        search_button.pack(fill="x", padx=5, pady=5)

        for f in fonts:
            listbox.insert(tk.END, f)
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=listbox.yview)


        def on_selection(event):
            selection = event.widget.curselection()
            if selection:
                index = selection[0]
                self.current_font = event.widget.get(index)
                self.text.configure(font=(self.current_font, self.font_size))
                self.update_font_info_label()
                

        listbox.bind("<<ListboxSelect>>", on_selection)

        search_entry.bind("<KeyRelease>", lambda event: update_list())

    def on_font_window_close(self):
        
        self.font_window.destroy()
        self.font_window = None 
        



    def change_font_size(self):
        if hasattr(self, 'size_window_open') and self.size_window_open:
            return  
        self.size_window_open = True  

        size_window = tk.Toplevel(self.master)
        size_window.title("Font Size")
        size_window.configure(bg='#e7c22b')
        size_window.geometry("230x200")
        size_window.resizable(False, False)  
    
        
        icon_path = "images/camelicon.ico" 
        if os.path.exists(icon_path):
            size_window.iconbitmap(icon_path)
        else:
            print("Icon file not found: ", icon_path)
    
        size_slider = tk.Scale(size_window, from_=8, to=48, orient="horizontal", label="Font Size", bg='#e7c22b')
        size_slider.set(self.font_size)
        size_slider.pack(padx=10, pady=40)

        def confirm():
            self.font_size = size_slider.get()
            self.text.config(font=(self.text.cget("font").split(' ')[0], self.font_size))
            self.update_font_info_label()
            

        def on_close():
            self.size_window_open = False  
            size_window.destroy()

        size_window.protocol("WM_DELETE_WINDOW", on_close)  

        confirm_button = tk.Button(size_window, text="Set Size", command=confirm, bg='#d9d8d7')
        confirm_button.pack(pady=10)



    def encrypt_text(self):
        text_to_encrypt = self.text.get("1.0", "end-1c")

        
        if not text_to_encrypt.strip():
            messagebox.showwarning("Warning", "There is no text to encrypt.")
            return

        
        encrypted_text = self.cesar_cipher(text_to_encrypt, shift=3)  

        
        self.show_encrypted_text(encrypted_text)

    def show_encrypted_text(self, encrypted_text):
        
        encrypted_text_window = tk.Toplevel(self.master)
        encrypted_text_window.title("Encrypted Text")

        
        icon_path = "images/camelicon.ico" 
        if os.path.exists(icon_path):
            encrypted_text_window.iconbitmap(icon_path)

        
        encrypted_text_widget = tk.Text(encrypted_text_window, wrap="word", bg=self.bg_color,
                                        font=(self.current_font, self.font_size))
        encrypted_text_widget.insert("1.0", encrypted_text)
        encrypted_text_widget.pack(expand=True, fill="both")

    def decrypt_text(self):
        
        encrypted_text = self.text.get("1.0", "end-1c")

        
        if not encrypted_text.strip():
            messagebox.showwarning("Warning", "There is no encrypted text to decrypt.")
            return

        
        decrypted_text = self.cesar_cipher(encrypted_text, shift=-3) 

        
        self.show_decrypted_text(decrypted_text)

    def show_encrypted_text(self, encrypted_text):
        
        encrypted_text_window = tk.Toplevel(self.master)
        encrypted_text_window.title("Encrypted Text")

        
        icon_path = "images/camelicon.ico"  
        if os.path.exists(icon_path):
            encrypted_text_window.iconbitmap(icon_path)

        
        encrypted_text_widget = tk.Text(encrypted_text_window, wrap="word", bg=self.bg_color,
                                    font=(self.current_font, self.font_size), fg=self.text.cget("fg"))
        encrypted_text_widget.insert("1.0", encrypted_text)
        encrypted_text_widget.pack(expand=True, fill="both")

    @staticmethod
    def cesar_cipher(text, shift):
       
        encrypted_text = ""
        for char in text:
            if char.isalpha():
                shifted = ord(char) + shift
                if char.islower():
                    if shifted > ord('z'):
                        shifted -= 26
                    elif shifted < ord('a'):
                        shifted += 26
                elif char.isupper():
                    if shifted > ord('Z'):
                        shifted -= 26
                    elif shifted < ord('A'):
                        shifted += 26
                encrypted_text += chr(shifted)
            else:
                encrypted_text += char
        return encrypted_text



    def confirm_create_file(self):
        
        response = messagebox.askyesno("New Document", "Do you want to create a new document?")
        if response:
            self.create_file()

    def create_file(self):
        self.text.delete("1.0", tk.END)
        self.current_file = None

    def open_file(self):
        
        file_path = filedialog.askopenfilename(defaultextension=".NC", filetypes=[("nomadcamel", "*.NC"), ("Todos los archivos", "*.*")])
        if file_path:
            
            with open(file_path, "r") as file:
                content = file.read()
                self.text.delete("1.0", tk.END)
                self.text.insert(tk.END, content)
            self.current_file = file_path



    def save_file_as(self):
        
        file_path = filedialog.asksaveasfilename(defaultextension=".NC", filetypes=[("nomadcamel", "*.NC"), ("Todos los archivos", "*.*")])
        if file_path:
            
            if not file_path.endswith(".NC"):
                file_path += ".NC"
            
            with open(file_path, "w") as file:
                file.write(self.text.get("1.0", tk.END))
            self.current_file = file_path



    def on_closing(self):
        
        if self.text.get("1.0", tk.END).strip() != "":
            response = messagebox.askyesnocancel("Close", "Do you want to save the file before closing?")
            if response is not None:
                if response:  
                    self.save_file_as()
                else:
                    self.close_window()  
            else:
                return  
        else:
            self.close_window() 

        
        if self.close_sound is not None:
            self.close_sound.play()
            
            sound_file_path = self.close_sound.get_length()
            if sound_file_path:
                threading.Timer(sound_file_path, self.close_window).start()
            else:
                print("No se pudo obtener la duración del sonido.")
                self.close_window() 

    def close_window(self):
        self.master.destroy() 

    def play_close_sound(self):
        if self.close_sound is not None:
            self.close_sound.play()
        else:
            print("El sonido de cierre no está disponible.")




    def change_bg_color(self):
        color = colorchooser.askcolor(title="Choose Background Color")[1]
        if color:
            self.bg_color = color
            self.master.configure(bg=color)
            self.text.configure(bg=color)

    def change_text_color(self):
        color = colorchooser.askcolor(title="Choose Text Color")[1]
        if color:
            self.text.configure(fg=color)



    def save_configuration(self):
        
        config_file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Archivos de configuración", "*.json")])
        if config_file_path:
            
            if hasattr(self, 'current_font') and self.current_font:
                font_family = self.current_font
            else:
                font_family = "Helvetica"  
            
            config_data = {
                "background_color": self.bg_color,
                "text_color": self.text.cget("fg"),
                "font_family": font_family,
                "font_size": self.font_size
            }
            with open(config_file_path, "w") as config_file:
                json.dump(config_data, config_file)



    def load_configuration(self):
        
        config_file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("Archivos de configuración", "*.json")])
        if config_file_path:
            with open(config_file_path, "r") as config_file:
                config_data = json.load(config_file)
                self.bg_color = config_data.get("background_color", "#FFFFFF")
                text_color = config_data.get("text_color", "#000000")
                font_family = config_data.get("font_family", "Helvetica")
                font_size = int(config_data.get("font_size", 12))
            
                self.master.configure(bg=self.bg_color)
                self.text.configure(bg=self.bg_color, fg=text_color, font=(font_family, font_size))
                self.update_font_info_label()
                self.font_size = font_size 
                self.current_font = font_family 

    def restore_default_configuration(self):
        
        default_bg_color = "#e7c22b"
        default_text_color = "#000000"
        default_font_family = "Helvetica"
        default_font_size = 12
    
        self.master.configure(bg=default_bg_color)
        self.text.configure(bg=default_bg_color, fg=default_text_color, font=(default_font_family, default_font_size))
        self.bg_color = default_bg_color
        self.font_size = default_font_size
        self.current_font = default_font_family



if __name__ == "__main__":
    root = tk.Tk()
    app = NotepadApp(root)
    root.mainloop()
