# Proposal G1-P03

I separated an empty lookup from unavailable storage at the connection boundary. The read opens an existing database and lets storage errors reach its caller; an initialized store can still report that the requested identifier is absent. The URI construction also needs scrutiny for filenames containing reserved characters. No initialization or recovery step is hidden inside this read.
