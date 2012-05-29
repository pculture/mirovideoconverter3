import gtk.gdk

class Image(gtk.gdk.Pixbuf):

    @classmethod
    def from_file(klass, filename):
        pb = gtk.gdk.pixbuf_new_from_file(filename)
        width = pb.get_width()
        height = pb.get_height()
        i = Image(pb.get_colorspace(), pb.get_has_alpha(), pb.get_bits_per_sample(),
                  width, height)
        pb.copy_area(0, 0, width, height, i, 0, 0)
        i.width = width
        i.height = height
        return i


