from dash import dcc

class Config:

    def __init__(self, conn):
        self.conn = conn

    def layout(self):
        return dcc.Markdown("""
                ```
                # Parametros Discogs: 
        
                ## query
                string (optional) Example: nirvana

                Search query

                ## type
                string (optional) Example: release

                String. One of release, master, artist, label

                ## title
                string (optional) Example: nirvana - nevermind

                Search by combined “Artist Name - Release Title” title field.

                ## release_title
                string (optional) Example: nevermind

                Search release titles.

                ## credit
                string (optional) Example: kurt

                Search release credits.

                ## artist
                string (optional) Example: nirvana

                Search artist names.

                ## anv
                string (optional) Example: nirvana

                Search artist ANV.

                ## label
                string (optional) Example: dgc

                Search label names.

                ## genre
                string (optional) Example: rock

                Search genres.

                ## style
                string (optional) Example: grunge

                Search styles.

                ## country
                string (optional) Example: canada

                Search release country.

                ## year
                string (optional) Example: 1991

                Search release year.

                ## format
                string (optional) Example: album

                Search formats.

                ## catno
                string (optional) Example: DGCD-24425

                Search catalog number.

                ## barcode
                string (optional) Example: 7 2064-24425-2 4

                Search barcodes.

                ## track
                string (optional) Example: smells like teen spirit

                Search track titles.

                ## submitter
                string (optional) Example: milKt

                Search submitter username.

                ## contributor
                string (optional) Example: jerome99

                Search contributor usernames.

                ```

        
        """)