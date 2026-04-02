# First we check if the necessary tools are installed
HELP="Usage: bash ./install.sh -install || bash ./install.sh -add"; 
# File for download the required models
MODEL_FILE="$(pwd)/setup/models.txt";
REQS="$(pwd)/setup/requirements.txt";

if [ $# -ne 1 ]; then
       echo "${HELP}";
       exit 1;
fi

case $1 in
	-add)

		if ! command -v ollama >/dev/null 2>&1; then
			echo "Be sure to run ./setup.sh -install before trying to add anything."
			exit 1;
		fi 

		while IFS= read -r model || [[ -n "$model" ]]; do
			model=$(echo "$model" | xargs);
			[[ -z "$model" || "$model" == \#* ]] && continue

			echo "pulling model: $model";
			ollama pull $model;
		done < $MODEL_FILE;

		echo "Installed all the additional models.";
		exit 1;;

	-install)
		;;
	*)
		echo "${HELP}";
		exit 1;;
esac

# We make sure python3 is installed
if ! command -v python3 >/dev/null 2>&1;
then
	echo "Make sure that python3 is installed.";
	exit 1;
fi

# Make sure EnergiBridge is installed
if ! command -v energibridge >/dev/null 2>&1;
then
	echo "Make sure that EnergiBridge is installed.";
	exit 1;
fi

echo "Prerequisites python3 and EnergiBridge have correctly been installed.";

python3 -m venv ../.venv;
source ../.venv/bin/activate;

pip3 install -r $REQS

# Ask the user whether they want to install ollama and the basic models
read -p "The script is about to install ollama (if not installed yet) and llm models for the tool. This will require about 15 Gb of diskspace. Would you like to continue? [y/n]" confirm
if [[ "$confirm" =~ [yY] ]]; then
	echo "proceeding the installation.";
else
	echo "aborting.";
	exit 1;
fi

# Download ollama
if ! command -v ollama >/dev/null 2>&1;
then 
	echo "Downloading ollama...";
	curl -fsSL https://ollama.com/install.sh | sh
fi

# Create a file with the basic models that will be used
if [[ ! -f $MODEL_FILE ]]; then
cat <<EOF > models.txt
# Basic models
gemma3:4b 
gemma3:12b 

# Add your own here
EOF
fi

echo "Downloading the models..."

while IFS= read -r model || [[ -n "$model" ]]; do
	model=$(echo "$model" | xargs);
	[[ -z "$model" || "$model" == \#* ]] && continue

	echo "pulling model: $model";
	ollama pull $model;
done < $MODEL_FILE;

echo "All models were successfully installed."

# The tool is turned into an executable
chmod +x ./efficientLLM






