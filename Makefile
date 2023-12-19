# Makefile for building Scratch VM and GUI

# Variables
SRC_HOME = /usr/app
VM_DIR = $(SRC_HOME)/scratch-vm
GUI_DIR = $(SRC_HOME)/scratch-gui
BUILD_SCRIPTS = ./2-build.sh
RUN_SCRIPTS = ./3-run-private.sh

# Targets
all: install-dependencies build 

install-dependencies:
	git clone --depth=1 https://github.com/LLK/scratch-vm.git $(VM_DIR)
	git clone --depth=1 https://github.com/LLK/scratch-gui.git $(GUI_DIR)

build: build-vm build-gui

build-vm:
	echo "Building Scratch VM..."
	cd $(VM_DIR) && npm install && npm ln

build-gui:
	echo "Building Scratch GUI..."
	cd $(GUI_DIR) && npm install && npm ln scratch-vm

run:
	echo "Copying extension development files..."
	cp $(BUILD_SCRIPTS) $(SRC_HOME)
	cp $(RUN_SCRIPTS) $(SRC_HOME)
	echo "Running Setup"
	./setup.sh
	echo "Running build + server"
	./2-build.sh
	./3-run-private.sh

# Phony targets
.PHONY: all build build-vm build-gui copy-scripts