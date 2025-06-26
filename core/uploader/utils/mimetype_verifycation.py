import magic

class VerifyFiles:
    mime = magic.Magic(mime=True)
    def VerifyImages(file):
        mimetype = VerifyFiles.mime.from_file(file)
        if mimetype in ("image/jpeg", "image/png"):
            return True
        return False
    