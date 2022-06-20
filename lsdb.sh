# -*- coding: utf-8 -*-
#
#   lsdb is a meta-data multi-tool
#
#	filesystem meta-data --> database (postgres)
#
#  	Copyright (C) 2020 Terrestrial Downlink LLC 
#	       <https://www.terrestrialdownlink.org>
#
#	function lsdb
#

function lsdb() { 

	findpath=$( /Users/donb/coreutils-9.0/src/realpath "$1" )
	#echo "   findpath == "$findpath
	
	#/Users/donb/coreutils-9.0/src/realpath -z "$1" # -z is no trailing CR

	uname=$(uname -s) 
        case "$uname" in
        Darwin) #echo "uname == Darwin"
		VOL=$(df "$1" | grep -v "^Filesystem" | cut -f 1 -d " ")
		#echo "        VOL == "$VOL
		VOLNAME=$(diskutil info "$VOL" | grep  "Volume Name" | cut -b 30- )
		#echo "    VOLNAME == "$VOLNAME
		VOLUUID=$(diskutil info $VOL | grep "Volume UUID" | awk '{print $3}')
		#echo "    VOLUUID" "==" $VOLUUID

		if [ -z "${MACHINEID}" ]; then #  "MACHINEID is unset or set to the empty string"
	    	    MACHINEID=$( system_profiler SPHardwareDataType  | grep -e "Hardware UUID:" | \
				cut -b 22- )
		    #echo "  MACHINEID" "<=" $MACHINEID
		#else # non-empty string 
		    #echo "  MACHINEID" "==" $MACHINEID
		fi


		#findpathhash=$( md5 -q "$findpath")
		#echo "findpathhash" "==" $findpathhash
           	;;
        FreeBSD) echo "$uname = FreeBSD" 
           ;;
        sh) echo "$uname : Shell script"
            ;;
        txt) echo "$uname : Text file"
             ;;
        *) echo " $uname : Not processed"
           ;;
	esac




	PROCESSID=$$
	#echo "PROCESSID" "==" $PROCESSID


	DATETIMEUTC=$(python2.7 -c "import datetime ; \
			print datetime.datetime.utcnow().isoformat()+\"+00\"")
	#echo "DATETIMEUTC" "==" $DATETIMEUTC

		# 	'%i		inode
		# 		%s	total size (bytes)
		# 		%X	 last access (seconds)
		# 		%W	mod, create, birth,
		# 		%Y,
		# 		%Z,
		# 		%F	file type
		# 		%n 	file path
		# 		\0' 
		
		#              %Ak    File's last access time in the  format  specified  by  k,  which  is
		#               %Bk    File's  birth time, i.e., its creation time, in the format specified
		#               %Ck    File's  last  status change time in the format specified by k, which
		#               %i     File's inode number (in decimal).
		#               %p     File's name.
		#               %s     File's size in bytes.
		#               %Tk    File's last modification time in the format specified by k, which is
		#               %y     File's type (like in ls -l), U=unknown type (shouldn't happen)
		# 
		# 	       -print0, -fprint0
		#   		Always print the exact filename, unchanged, even if the output is going  to
		#  					 a terminal.


	# stat offers different c style quoting, eg
	#	'/Users/donb/test_files/'\''single "quoted"'\''.txt'
	#	'/Users/donb/test_files/embedded'$'\026\n''return.txt'
	#	'/Users/donb/test_files/return'$'\016''embedded.txt'
	#  but none of these are CSV-style, double quotes around doubled-double quotes (if inside)
	#  gnu stat can terminate (its output of) a record with \0

 	# gfind "$findpath" -printf "$MACHINEID,$DATETIMEUTC,$PROCESSID,$VOLUUID,%i,%s,%As,%Bs,%Cs,%Ts,%y,\"%p\"\n" | \

		#find "$findpath"  -print0 | \
		#xargs -0 -I {} /Users/donb/coreutils-9.0/src/stat  \
			#--printf='%i,%s,%X,%Y,%Z,%W,%F,%n\0' "{}" | \
 	gfind "$findpath" -printf "%i,%s,%As,%Bs,%Cs,%Ts,%y,%p\0" | \
		gawk -v VID=$VOLUUID -v MID=$MACHINEID -v PID=$PROCESSID -v TID=$DATETIMEUTC \
			'BEGIN { RS="\0"; FS=","; OFS=","  } \
				{
				XX=1+length($1)+1+length($2)+1+length($3)+1+length($4)+1+length($5)+1+length($6)+1+length($7)+1
				SS=substr($0,XX)
				gsub("\"","\"\"",SS) # substitute "in place"
				print MID,TID,PID,VID,$1,$2,$3,$4,$5,$6,$7,"\""SS"\"";
				}' | \
	/usr/local/opt/postgresql@12/bin/psql  files  \
				-c "copy u12 from STDIN  with (format csv);" 


}


#	${parameter :−word }
#	If parameter is unset or null, the expansion of word is substituted. 
#	Otherwise, the value of parameter is substituted.
#	${parameter:+[word]}
#	Use Alternative Value. If parameter is unset or null, null shall be substituted; 
#	otherwise, the expansion of word (or an empty string if word is omitted) 
#	shall be substituted.
#
#	[from: 3.5.3 Shell Parameter Expansion << 3.5 Shell Expansions << 3 Basic Shell Features]


	# 	(gnu) stat        --printf=FORMAT
        #              like --format, but interpret backslash escapes, and do not
        #              output a mandatory trailing newline;

	#echo

        #find "$1"  \
		#-print0 | \
	#xargs -0 -I {} /Users/donb/coreutils-9.0/src/realpath -z "{}" | \
	#xargs -0 -I {} /Users/donb/coreutils-9.0/src/stat \
	#--printf="$VOLUUID,%i,%s,%X,%Y,%Z,%W,%F,%n\0" \
		#"{}" | \
	#gawk -v VID=$VOLUUID  MID=$MACHINEID\
		#'BEGIN { RS="\0"; FS=","; OFS=" -- "  } \
        	#{
        	#ll=length($0)
        	#XX=9+length($1)+length($2)+length($3)+length($4)+length($5)+length($6)+length($7)+length($8)
        	#SS=substr($0,XX)
        	#ZZ=gsub("\"","\"\"",SS)

		#"md5 -q "SS | getline MM
		#print "MM", MM
#

        	#print VID,MM,ll,XX,$1,$2,$3,$4,$5,$6,$7,"\""$8"\"","<<"SS">>";
        	#}'
