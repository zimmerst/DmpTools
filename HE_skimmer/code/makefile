DMPSWRELEASE  = DmpSoftware-6-0-0
DMPSWPATH = /cvmfs/dampe.cern.ch/centos7/opt/DMPSW/
# Root variables
ROOTCFLAGS   := $(shell root-config --cflags)
ROOTLIBS     := $(shell root-config --libs) 
#-lMinuit -lProof

# Programs
CXX          = g++ 
CXXFLAGS     = -g -Wall -fPIC -Wno-deprecated -ggdb -Wno-reorder -Wno-return-type -Wno-unused-but-set-variable
LDFLAGS      = -g -lm
SOFLAGS      = -shared 

# Local Includes
#INCDIR      += -Iincludes -I/atlas/software/dampe/centos7/DmpSoftware/Event/include
INCDIR      += -Iincludes -I${DMPSWPATH}/${DMPSWRELEASE}/include

# Libraries
DMPLIBDIR = -L${DMPSWPATH}/${DMPSWRELEASE}/lib
DMPLIBS = -lDmpKernel `ls ${DMPSWPATH}/${DMPSWRELEASE}/lib/ | grep so | grep -v Kernel | sed -e 's/lib/-l/g' | sed -e 's/\.so//g' | tr '\n' ' '`
#DMPLIBS   = -lDmpEvent
LIBS      += $(ROOTLIBS) ${DMPLIBDIR} ${DMPLIBS}
#LIBS      += $(ROOTLIBS) -L/atlas/software/dampe/centos7/DmpSoftware/Event -lDmpEvent

# Direct to make the directories with the sources:
VPATH  = ./lib / ./bin ./app ./includes 

# Assign or Add variables
CXXFLAGS    += $(ROOTCFLAGS)
CXXFLAGS    += $(INCDIR)
CXXFLAGS    += $(LIBS)

GARBAGE      = *~ ./*/*~ lib/*.so lib/*.o ./*/*.o ./*.o

############################################################################
# Build main.c compiling only the first prereq: ($<) means main.c
############################################################################

main : main.o 

############################################################################
# General rules. Some of them need not be specified due to implicit rules, 
# but are here redefined to add an "echo"
############################################################################

%.o : %.cc %.h
	@echo "compiling $<"
	@echo "$(CXX) $(CXXFLAGS) -c $<"
	@$(CXX) $(CXXFLAGS) -c $< 

%.o : %.cc 
	@echo "compiling $<"
	@echo "$(CXX) $(CXXFLAGS) -c $<"
	@$(CXX) $(CXXFLAGS) -c $< 

%.o : %.h
	@echo "compiling $<"
	@echo "$(CXX) $(CXXFLAGS) -c $<"
	@$(CXX) $(CXXFLAGS) -c $< 

%   : %.o
	@echo "compiling and linking $@"
	@echo "$(CXX) $(CXXFLAGS) $^ -o $@"
	@$(CXX) $(CXXFLAGS) $^ -o $@	
	@if [ `ls | grep "\.so"$ | wc -l` != 0 ]; then mv *.so lib/; fi
	@if [ `ls | grep "\.o"$  | wc -l` != 0 ]; then mv *.o  lib/; fi
	@mv $@ bin/

############################################################################
# Phony rules (no prerequisites)
############################################################################

clean :
	@rm -f $(GARBAGE)


