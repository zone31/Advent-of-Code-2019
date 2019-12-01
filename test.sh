RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color
SPACING='  '
#Ohwee slamkode
function compare {
    wanted=$1
    got=$2
    title=$3
    if [ "$wanted" == "$got" ]; then
       echo -e "  " $title "${GREEN}Correct!${NC}"
    else
       echo -e "  " $title "${RED}Incorrect!${NC}"
       echo "WANTED"
       echo $wanted
       echo "____"
       echo "GOT"
       echo $got
       echo "____"
    fi
}

for day in {1..25} ; do
    for folder in Days/$day/*/ ; do
        if [[ $folder == *\*/ ]] ;
        then
            printf "Day %s %s ${RED}not found!${NC}\n" $day "${SPACING:${#day}}"
        else
            res1=$(cat Days/$day/star1.txt)
            res2=$(cat Days/$day/star2.txt)
            case "$folder" in
                *Python/)
                    printf "Day %s %s ${YELLOW}Python${NC}\n" $day "${SPACING:${#day}}"
                    pushd $folder > /dev/null
                    star1=$(python3 run.py 1)
                    star2=$(python3 run.py 2)
                    compare $res1 $star1 "Star 1"
                    compare $res2 $star2 "Star 2"
                    popd > /dev/null
                    ;;
                *Haskell/)
                    echo -e "Day $day ${GREEN}Haskell${NC}"
                    ;;

                *)
                    echo "Language in $folder not implemented!"
            esac
        fi
        #echo $folder
    done
done