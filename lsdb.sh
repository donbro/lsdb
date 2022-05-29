#
#	function lsdb

#
#	initialize (and export) the machine ID
#	  next call of function lsdb() will use initialized shell varible MACHINEID
#	  next call of source lsdb.sh will re-initialized 
#

#	${parameter :−word }
#	If parameter is unset or null, the expansion of word is substituted. 
#	Otherwise, the value of parameter is substituted.
#	${parameter:+[word]}
#	Use Alternative Value. If parameter is unset or null, null shall be substituted; 
#	otherwise, the expansion of word (or an empty string if word is omitted) 
#	shall be substituted.
#
#	[from: 3.5.3 Shell Parameter Expansion << 3.5 Shell Expansions << 3 Basic Shell Features]

#MACHINEID=$( system_profiler SPHardwareDataType  | grep -e "Hardware UUID:" | cut -b 22- )
set MACHINEID
function lsdb() { 

	echo "lsdb $1"

	echo "      uname == $(uname -s)" 

	VOL=$(df "$1" | grep -v "^Filesystem" | cut -f 1 -d " ")
	echo "        VOL == "$VOL

	VOLNAME=$(diskutil info "$VOL" | grep  "Volume Name" | cut -b 30- )
	echo "    VOLNAME == "$VOLNAME

	VOLUUID=$(diskutil info $VOL | grep "Volume UUID" | awk '{print $3}')
	echo "    VOLUUID" "==" $VOLUUID

	if [ -z "${MACHINEID}" ]; then
	   # echo "MACHINEID is unset or set to the empty string"
	    MACHINEID=$( system_profiler SPHardwareDataType  | grep -e "Hardware UUID:" | \
				cut -b 22- )
		echo "  MACHINEID" "<=" $MACHINEID
	else
	    #echo "MACHINEID is set to a non-empty string ($MACHINEID)"
		echo "  MACHINEID" "==" $MACHINEID
	fi



	echo "  PROCESSID" "==" $$

	DATETIMEUTC=$(python2.7 -c "import datetime ; \
			print datetime.datetime.utcnow().isoformat()")

	echo "DATETIMEUTC" "==" $DATETIMEUTC

	find "$1"

	FILEHASH=$( md5 -q "$1")

	echo "   FILEHASH" "==" $FILEHASH

	# 	(gnu) stat        --printf=FORMAT
        #              like --format, but interpret backslash escapes, and do not
        #              output a mandatory trailing newline;

        find "$1"  -print0 | \
	  xargs -0 -I {} /Users/donb/coreutils-9.0/src/stat \
		--printf="$VOLUUID,%i,%s,%X,%Y,%Z,%W,%F,%n\n" "{}" 

return
        find "$1"  -print0 | \
	  xargs -0 -I {} /Users/donb/coreutils-9.0/src/stat \
		--printf="$VOLUUID,%i,%s,%X,%Y,%Z,%W,%F,%n\0" "{}" | \
	  gawk -v VID=$VOLUUID 'BEGIN { RS="\0"; FS=","; OFS=" -- "  } \
        	{
        	ll=length($0)
        	XX=9+length($1)+length($2)+length($3)+length($4)+length($5)+length($6)+length($7)+length($8)
        	SS=substr($0,XX)
        	ZZ=gsub("\"","\"\"",SS)

        	print VID,ll,XX,$1,$2,$3,$4,$5,$6,$7,"\""$8"\"","<<"SS">>"
        	}'

}


