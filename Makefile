RES_SRC = res/resources.qrc
RES_OUT = src/resources_rc.py

all: build

build: $(RES_OUT)

$(RES_OUT): $(RES_SRC)
	pyside6-rcc $(RES_SRC) -o $(RES_OUT) 

clean:
	rm -f $(RES_OUT)

.PHONY: all build clean
