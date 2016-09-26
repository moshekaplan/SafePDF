"""
SafePDF

Makes untrusted PDF files safe!

SafePDF does this by converting the PDF to a series of images
The raw text is included in the PDF an embedded file, so as to maintain searching.

Written by Moshe Kaplan
November 13, 2014

Dependencies:
Wand (http://wand-py.org)
PyPDF2 (https://github.com/mstamy2/PyPDF2)
"""

# Built in modules
import sys
import StringIO

# 3rd-party modules
import PyPDF2
import wand.image


def make_safe(src_fname, dest_fname):
    # Read in the PDF
    with open(src_fname, 'rb') as fh:
        src_pdf_blob = fh.read()

    # Convert each page to its own PDF
    with wand.image.Image(blob=src_pdf_blob, format='pdf', resolution=300) as src_pdf_image:
        pages = []
        for page in src_pdf_image.sequence:
            pages.append(page.clone().convert('pdf').make_blob())

    # Merge the pages together with PyPDF2
    dest_pdf = PyPDF2.PdfFileMerger()
    for page in pages:
        dest_pdf.append(StringIO.StringIO(page))

    # Extract text and merge into one large string:
    # Note: This functionality requires an updated version of PyPDF2
    if hasattr(dest_pdf.output, 'addAttachment'):
        texts = []
        pdf = PyPDF2.PdfFileReader(StringIO.StringIO(src_pdf_blob))
        for page_num, page in enumerate(pdf.pages):
            texts.append(page.extractText())

        total_text = '\n'.join(texts)

        # Attach the text to the PDF
        dest_pdf.output.addAttachment('contents.txt', total_text)

    # Write PDF file to disk
    with open(dest_fname, 'wb') as dest_fh:
        dest_pdf.write(dest_fh)


def main():
    if len(sys.argv) < 2:
        print "Usage: %s sourcefile" % sys.argv[0]
        sys.exit(0)

    src_fname = sys.argv[1]
    dest_fname = sys.argv[1] + '_safe.pdf'

    make_safe(src_fname, dest_fname)

if __name__ == "__main__":
    main()
