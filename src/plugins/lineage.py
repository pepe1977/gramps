#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007       Jerome Rapinat, B. Malengier
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id: _FamilyList.py 8897 2007-08-30 19:49:04Z bmcage $

"""
Display a person's father or mother lineage
"""

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------

import RelLib
from Simple import SimpleAccess, SimpleDoc
from gettext import gettext as _
from PluginUtils import register_quick_report
from ReportBase import CATEGORY_QR_PERSON

__FMT     = "%-30s\t%-12s\t%-12s"
__FMT_rem = "   %s: %s"

def run_father(database, document, person):
    
    sa = SimpleAccess(database)
    sd = SimpleDoc(document)

    # display the results

    sd.title(_("Father lineage for %s") % sa.name(person))
    sd.paragraph("")
    sd.paragraph(_(""
        "This report shows the father lineage, also called patronymic lineage"
        " or Y-line."
        " People in this lineage all share the same Y-chromosone."
        ))
    sd.paragraph("")
    
    sd.header2(__FMT %(_("Name Father"),_("Birth Date"),_("Death Date")))
    sd.paragraph("")
    
    make_details(RelLib.Person.MALE, person, sa, sd, database)
    
    sd.paragraph("")
    sd.paragraph("")
    
    sd.header2((_("Sons")))
    sd.paragraph("")
    
    make_details_child(RelLib.Person.FEMALE, person, sa, sd, database)
    
def run_mother(database, document, person):
    
    sa = SimpleAccess(database)
    sd = SimpleDoc(document)

    # display the results

    sd.title(_("Mother lineage for %s") % sa.name(person))
    sd.paragraph("")
    sd.paragraph(_(""
        "This report shows the mother lineage, also called matronymic lineage "
        "or M-line."
        " People in this lineage all share the same RNA."
        ))
    sd.paragraph("")
    
    sd.header2(__FMT %(_("Name Mother"),_("Birth"),_("Death Date")))
    sd.paragraph("")
    
    make_details(RelLib.Person.FEMALE, person, sa, sd, database)
    
    sd.paragraph("")
    sd.paragraph("")
    
    sd.header2((_("Daughters")))
    sd.paragraph("")
    
    make_details_child(RelLib.Person.FEMALE, person, sa, sd, database)
    
def make_details(gender, person, sa, sd, database) :
    # loop as long as there are fathers/mothers
    rem_str = ""
    while person:
        person_handle = person.handle
        sd.paragraph(__FMT % (sa.name(person), sa.birth_date(person),
                            sa.death_date(person)))
        if rem_str:
            sd.paragraph(__FMT_rem % (_("Remark"), rem_str))
            
        # obtain the first father/mother we find in the list
        parent_handle_list = person.get_parent_family_handle_list()
        person = None
        for parent in parent_handle_list:
            rem_str = ""
            family_id = parent_handle_list[0]
            family = database.get_family_from_handle(family_id)
            if gender == RelLib.Person.MALE :
                person = database.get_person_from_handle(
                            family.get_father_handle())
            else :
                person = database.get_person_from_handle(
                            family.get_mother_handle())
            childrel = [(ref.get_mother_relation(), 
                            ref.get_father_relation()) for ref in 
                            family.get_child_ref_list() 
                            if ref.ref == person_handle]
            if not childrel[0][1] == RelLib.ChildRefType.BIRTH :
                rem_str = add_rem(rem_str, _("No birth relation with child"))
            if person and person.gender == gender :
                break
            elif person and person.gender == RelLib.Person.UNKNOWN :
                rem_str = add_rem(rem_str, _("Unknown gender"))
                break
            else :
                person = None

def make_details_child(gender, person, sa, sd, database) :
    #recursively called function
    def make_child_line(person, prepend) :
        rem_str = ""
        if person.gender == RelLib.Person.UNKNOWN :
            rem_str = add_rem(rem_str, _("Unknown gender"))
            
        if rem_str : 
            rem_str = _("Remark")+": "+rem_str
        front = ""
        if prepend :
            front = prepend + "-"
        sd.paragraph(front + "%s (%s - %s) %s" % (sa.name(person),
                            sa.birth_date(person),
                            sa.death_date(person), rem_str))
            
        family_handles = person.get_family_handle_list()
        for fam_handle in family_handles :
            fam = database.get_family_from_handle(fam_handle)
            childrel = [(ref.ref, ref.get_mother_relation(), 
                        ref.get_father_relation()) for ref in 
                            fam.get_child_ref_list()]
            for child in childrel: 
                if gender == RelLib.Person.FEMALE and \
                        not child[1] == RelLib.ChildRefType.BIRTH :
                    continue
                if gender == RelLib.Person.MALE and \
                        not child[2] == RelLib.ChildRefType.BIRTH :
                    continue
            
                person = database.get_person_from_handle(child[0])
                if person and person.gender == gender :
                    make_child_line(person, prepend + '  |')
                    
    # loop over all children of gender and output
    prev_str = ""
    rem_str = ""
    make_child_line(person,prev_str)
    
    
def add_rem(remark, text):
    if remark:
        return remark + ', ' + text
    else:
        return text
  
#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------

register_quick_report(
    name = 'father_lineage',
    category = CATEGORY_QR_PERSON,
    run_func = run_father,
    translated_name = _("Father lineage"),
    status = _("Stable"),
    description= _("Display father lineage"),
    author_name="B. Malengier",
    author_email="benny.malengier@gramps-project.org"
    )

register_quick_report(
    name = 'mother_lineage',
    category = CATEGORY_QR_PERSON,
    run_func = run_mother,
    translated_name = _("Mother lineage"),
    status = _("Stable"),
    description= _("Display mother lineage"),
    author_name="B. Malengier",
    author_email="benny.malengier@gramps-project.org"
    )
    