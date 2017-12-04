#!/bin/bash

printf "\n>>>> Execute build.bash \n\n"

release_name="`cat ../parameters.txt | grep dampe_sw_release | awk '{print $2}'`"
release_path="`cat ../parameters.txt | grep dampe_sw_path | awk '{print $2}'`"
system_type="`cat ../parameters.txt | grep system_type | awk '{print $2}'`"

source scripts/setup-externals_${system_type}.sh

echo ""
echo "which gcc $(which gcc)"
echo "which g++ $(which g++)"
echo "which ld $(which ld)"
echo "" 
echo "Use ${release_path}"
echo "Use ${release_name}"
echo ""
echo "Use ${ROOTSYS}"
echo ""

cat << EOF > tmp
DMPSWRELEASE  = ${release_name}
DMPSWPATH = ${release_path}
EOF

cat tmp mkf > makefile
#cat mkf > makefile
echo "creating directories"
mkdir -vp lib bin
mkdir -vp ../code/scripts/plots
make clean
make -j8

rm -f tmp
