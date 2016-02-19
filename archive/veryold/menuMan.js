DOM = (document.getElementById) ? 1 : 0;
NS4 = (document.layers) ? 1 : 0;
IE4 = (document.all) ? 1 : 0;

//
// Copyright (C) 2002, 2003 Rodd Clarkson
// 
// This program is free software; you can redistribute it and/or
// modify it under the terms of the GNU General Public License as
// published by the Free Software Foundation; either version 2 of the
// License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful, but
// WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
// 02111-1307, USA.
//

//var loaded = 0;			// to avoid stupid errors of Microsoft browsers

function raise(menuName,on) {
//	if (loaded) {	// to avoid stupid errors of Microsoft browsers
		if (on) {
			if (DOM) { document.getElementById(menuName).style.visibility = "visible"; }
			else if (NS4) { document.layers[menuName].visibility = "show"; }
			else { document.all[menuName].style.visibility = "visible"; }
		}
		else {
			if (DOM) { document.getElementById(menuName).style.visibility = "hidden"; }
			else if (NS4) { document.layers[menuName].visibility = "hide"; }
			else { document.all[menuName].style.visibility = "hidden"; }
		}
//	}
}



