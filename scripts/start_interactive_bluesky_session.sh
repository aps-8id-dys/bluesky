#!/bin/bash

# Function to display usage
usage() {
  echo "Usage: $0 [keyword]"
  echo "If no keyword is specified, you will be prompted to choose between the two options."
  echo "Valid keywords: ipython, jupyter"
  exit 1
}

# Function to handle the output for each keyword
handle_keyword() {
  case $1 in
    ipython)
      echo "You chose ipython!"
      ipython -i -c "%run bluesky_interactive_startup.ipy"
      ;;

    jupyter)
      echo "You chose jupyter!"
      echo "Sadly Eric has not finished that yet, try again later"
      # jupyter lab --NotebookApp.exec_files=['bluesky_interactive_startup.ipy']
      ;;
    *)
      echo "Invalid keyword. Please specify either 'ipython' or 'jupyter'."
      usage
      ;;
  esac
}

# Check for help flag
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
  usage
fi

# Check if a keyword was provided
if [ -z "$1" ]; then
  # No keyword provided, prompt the user
  echo "Please specify a keyword: ipython or jupyter"
  read -r keyword
  handle_keyword "$keyword"
else
  # Keyword provided, handle it
  handle_keyword "$1"
fi
