import os
import tempfile
import subprocess
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.pdfgen import canvas
import tkinter as tk
import webbrowser
from tkinter import filedialog


def _get_temp_filename():
    with tempfile.NamedTemporaryFile(suffix=".pdf") as fh:
        return fh.name


def sign_pdf(files):
    for file in files:
        output_filename = "{}_signed{}".format(*os.path.splitext(file))

        pdf_fh = open(file, 'rb')
        sig_tmp_fh = None

        pdf = PdfFileReader(pdf_fh)
        writer = PdfFileWriter()
        sig_tmp_filename = None
        sign_stamp = 'assets/sign_stamp.png'

        for i in range(0, pdf.getNumPages()):
            page = pdf.getPage(i)

            if i == pdf.getNumPages() - 1:
                # Create PDF for signature
                sig_tmp_filename = _get_temp_filename()
                c = canvas.Canvas(sig_tmp_filename, pagesize=page.cropBox)
                c.drawImage(sign_stamp, 50, 0, 500, 116, mask='auto')
                c.showPage()
                c.save()

                # Merge PDF in to original page
                sig_tmp_fh = open(sig_tmp_filename, 'rb')
                sig_tmp_pdf = PdfFileReader(sig_tmp_fh)
                sig_page = sig_tmp_pdf.getPage(0)
                sig_page.mediaBox = page.mediaBox
                page.mergePage(sig_page)

            writer.addPage(page)

        with open(output_filename, 'wb') as fh:
            writer.write(fh)

        for handle in [pdf_fh, sig_tmp_fh]:
            if handle:
                handle.close()
        if sig_tmp_filename:
            os.remove(sig_tmp_filename)

    # Open last file directory
    webbrowser.open(os.path.dirname(files[-1]))


def select_file():
    files = filedialog.askopenfilenames(
        initialdir='/', title='Select PDF File', filetypes=(('PDF files', '*.pdf'), ('All files', '*.*')))

    sign_pdf(files)


def show_options():
    win_options = tk.Toplevel(root)
    win_options.title('Options')
    win_options.geometry('400x200')
    root.withdraw()


root = tk.Tk()
root.title('Sign & Stamp PDF by Francis Ceril')
root.geometry('400x200')
root.resizable(False, False)

menubar = tk.Menu(root, bg='#f3f3f3', foreground='#111111',
                  activebackground='#f3f3f3', activeforeground='#111111', )
filemenu = tk.Menu(menubar, tearoff=0, bg='#f3f3f3',
                   foreground='#111111', font=('JetBrains Mono', 9, 'normal'))
filemenu.add_command(label='Options', command=show_options)
filemenu.add_separator()
filemenu.add_command(label='Exit', command=root.quit)

menubar.add_cascade(label='File', menu=filemenu)

button = tk.Button(root, text='Select PDF Files...', width=20, height=1, relief='flat', font=(
    'JetBrains Mono', 12, 'normal'), command=select_file)
button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

root.config(menu=menubar, bg='#2f4b4c')
root.mainloop()
