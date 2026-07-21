import datetime

# Store the next available id for all new attribs
LAST_ID = 0

# The usual OOP restrictions of Public, Protected, Private are not enforced in Python, everyhing is Public
# Instead, you are expected to indicate in your code which should be private etc and hope other programmers follow the principle (like a code of conduct pardon the pun)
# Prefix class vars with _ if you want to tell other programmers to treat them as private to class
# Prefix class vars with __ to make it more difficult by causing data mangling

class AttribStats:
    """Represent a key stats of an attribute within the data set. Match against a
    string in searches and store tags for each attrib."""

    def __init__(self, attribstatsname, ordered_stats_list, tags=""):
        """initialize an attrib with attribstats, associated stats field and optional
        space-separated tags. Automatically set the attribstats's creation date and a unique id."""
        self.attribname = attribstatsname
        self.minvalue = float(ordered_stats_list[0]) #min
        self.avgvalue = float(ordered_stats_list[1]) #mean
        self.medvalue = float(ordered_stats_list[2]) #med
        self.maxvalue = float(ordered_stats_list[3]) #max
        self.stdevalue = float(ordered_stats_list[4]) #stdev
        self.q1value = float(ordered_stats_list[5]) #quartile 1
        self.q3value = float(ordered_stats_list[6]) #quartile 3
        self.iqrvalue = float(ordered_stats_list[7]) #iqr
        self.tags = tags
        self.creation_date = datetime.date.today()
        global LAST_ID
        LAST_ID += 1
        self.id = LAST_ID

    def match(self, afilter):
        """Determine if this attribstats name matches the afilter
        text. Return True if it matches, False otherwise.

        Search is case sensitive and matches both text and
        tags.
        
        17Sep2024: Bug fix - afilter has to be an EXACT match to self.attribname
        not just 'in' self.attribname as some feature names are very similar to each other
        A match is not made with tags
        """
        return afilter == self.attribname

    def get_attrib_name(self):
        return self.attribname

    def get_min(self):
        return self.minvalue

    def get_avg(self):
        return self.avgvalue

    def get_med(self):
        return self.medvalue

    def get_max(self):
        return self.maxvalue

    def get_stdev(self):
        return self.stdevalue

    def get_q1(self):
        return self.q1value
    
    def get_q3(self):
        return self.q3value
    
    def get_iqr(self):
        return self.iqrvalue

    def get_full_attrib_details(self):
        """returns a dictionary containing attribname as key, and the list of stats associated with attribute."""
        dict_key = self.attribname
        
        dict_value = []
        dict_value.append(self.minvalue)
        dict_value.append(self.avgvalue)
        dict_value.append(self.medvalue)
        dict_value.append(self.maxvalue)
        dict_value.append(self.stdevalue)
        dict_value.append(self.q1value)
        dict_value.append(self.q3value)        
        dict_value.append(self.iqrvalue)
        
        attribstats_dict = {dict_key:dict_value}

        return attribstats_dict

    def get_attrib_stats(self):
        """returns a list of attrib stats."""
        attrib_summary_stats = []
        attrib_dict = self.get_full_attrib_details()
        attrib_summary_stats = attrib_dict[self.attribname]
        
        return attrib_summary_stats


class AttributeStatsBook:
    """Represent a collection of attributes with their stats for scaling purposes. Attribs can also be tagged and searched."""

    def __init__(self):
        """Initialize a data collection with an empty list."""
        self.attrib_statscollection = []

    def new_attrib(self, attribname, stats_list, tags=""):
        """Create a new scaled attrib and add it to the list."""
        self.attrib_statscollection.append(AttribStats(attribname, stats_list, tags))

    def _search(self, afilter):
        #Assumption: all attribs are unique
        attribstats = None
        for attribstats in self.attrib_statscollection:
            if attribstats.match(afilter):
                break
        return attribstats

    def get_attrib(self, attribname):
        #search the book for desired attrib stats and simply return the stats object or None
        attrib = self._search(attribname)
        return attrib
    
    def get_attrib_names_list(self):
        attrib_list = []
        for attribstats in self.attrib_statscollection:
            attrib_list.append(attribstats.get_attrib_name())
              
        return attrib_list

    def get_attrib_stats_list(self, attribname):
        #search the book for desired attrib stats and simply return the stats object or None
        attrib = self._search(attribname)

        return attrib.get_attrib_stats()

        

