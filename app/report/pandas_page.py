from math import ceil


class PandasPage(object):

    def __init__(self, frame=None, page=0, per_page=0, total=0):
        self.frame = frame
        self.page = page
        self.per_page = per_page
        self.total = total

    @property
    def displaying(self):
        """Display for the offset for the query"""
        return 'Showing {frm} to {where} records out of {total} records.'.format(
            frm=str((self.page - 1) * self.per_page),
            where=str(self.page * self.per_page),
            total=str(self.total)
        )

    @property
    def pages(self):
        """The total number of pages"""
        if self.per_page == 0 or not self.total:    # Handles empty frame or 0 per page
            pages = 0
        else:
            pages = int(ceil(self.total / float(self.per_page)))
        return pages

    @property
    def has_next(self):
        """True if a next page exists."""
        return self.page < self.pages

    @property
    def next_num(self):
        """Number of the next page"""
        if not self.has_next:
            return None
        return self.page + 1

    @property
    def prev_num(self):
        """Number of the previous page."""
        if not self.has_prev:
            return None
        return self.page - 1

    @property
    def has_prev(self):
        """True if a previous page exists"""
        return self.page > 1

    @property
    def has_next(self):
        """True if a next page exists."""
        return self.page < self.pages

    @property
    def next_num(self):
        """Number of the next page"""
        if not self.has_next:
            return None
        return self.page + 1
