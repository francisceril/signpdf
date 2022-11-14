#!/usr/bin/env python

import os
import time
import argparse
import tempfile
import PyPDF2
import datetime
from tkinter import *
from tkinter import filedialog
from reportlab.pdfgen import canvas

parser = argparse.ArgumentParser("Add signatures to PDF files")
parser.add_argument("pdf", help="The pdf file to annotate")
# parser.add_argument("signature", help="The signature file (png, jpg)")
# parser.add_argument("--date", action='store_true')
# parser.add_argument("--output", nargs='?',
#         help="Output file. Defaults to input filename plus '_signed'")
# parser.add_argument("--coords", nargs='?', default='1x200x0x170x100',
#         help="Coordinates to place signature. Format: PAGExXxYxWIDTHxHEIGHT.  1x200x300x125x40 means page 1, 200 units horizontally from the bottom left, 300 units vertically from the bottom left, 125 units wide, 40 units tall. Pages count starts at 1 (1-based indexing).  Units are pdf-standard units (1/72 inch).")


def _get_tmp_filename(suffix=".pdf"):
    with tempfile.NamedTemporaryFile(suffix=".pdf") as fh:
        return fh.name

def sign_pdf(pdfFile):
    output_filename = "{}_signed{}".format(
        *os.path.splitext(pdfFile.pdf)
    )

    pdf_fh = open(pdfFile.pdf, 'rb')
    sig_tmp_fh = None
    signature = "sign.png"

    pdf = PyPDF2.PdfFileReader(pdf_fh)
    writer = PyPDF2.PdfFileWriter()
    sig_tmp_filename = None

    for i in range(0, pdf.getNumPages()):
        page = pdf.getPage(i)

        if i == pdf.getNumPages() - 1:
            # Create PDF for signature
            sig_tmp_filename = _get_tmp_filename()
            c = canvas.Canvas(sig_tmp_filename, pagesize=page.cropBox)
            c.drawImage(signature, 200, 0, 170, 100, mask='auto')

            c.showPage()
            c.save()

            # Merge PDF in to original page
            sig_tmp_fh = open(sig_tmp_filename, 'rb')
            sig_tmp_pdf = PyPDF2.PdfFileReader(sig_tmp_fh)
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

def main():
    sign_pdf(parser.parse_args())

# def browsePdf():
#     filename = filedialog.askopenfilename(
#         initialdir = "/",
#         title = "Select PDF file",
#         filetypes= (("Text Files", "*.txt"), ("PDF Files", "*.pdf"))
#     )

#     labelFilename.config(text=filename)

# win = Tk()
# win.title("Sign PDF")
# win.geometry('500x400')


# labelFilename = Label(win, text="sample.pdf")
# labelFilename.grid(row=0)


# btnBrowse = Button(win, text="Open", command=browsePdf)
# btnBrowse.place(x=200, y=30)

# btnSign = Button(win, text="Sign", command=sign_pdf)
# btnSign.place(x=300, y=40)

# win.mainloop()

if __name__ == "__main__":
    main()
