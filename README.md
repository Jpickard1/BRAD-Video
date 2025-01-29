# BRAD-Video RAG
This repository deploys a [`BRAD`](https://github.com/Jpickard1/BRAD) agent to build a Retrieval Augementec Generation powered chatbot for youtube serieses. BRAD (Bioinformatics Retrieval Augmented Digital assistant) is an LLM powered chatbot that can be reconfigured to perform tasks ranging from database search and software execution, to helping search through a seminar series as we do here. The default settings of this system will build a RAG database for the University of Michigan [Department of Computational Medicine and Bioinformatics (DCMB) youtube channel](https://www.youtube.com/@universityofmichigancomput8877/featured), which feature several seminar series from 2017 until today (but this can be reconfigured).


https://github.com/user-attachments/assets/293d7bf0-5e6b-4bcb-b62b-e4b8fd17e65f



## Setup
Follow the below instructions to install the necessary dependencies and build the RAG database. This must be run one time when installing the system, and note that the dependencies identical to that of the [`BRAD` repository](https://github.com/Jpickard1/BRAD) with the addition of `scrapetube` and `youtube_transcript_api`.

### Install Dependencies

**Install BRAD**
This code must be run from the `video-rag` branch from the `BRAD` repository, and the roots of both repository must be located within the same directory. Run the below commands to install both repositories:
```
git clone https://github.com/Jpickard1/BRAD.git
cd BRAD
git checkout video-rag
cd ..
git clone https://github.com/Jpickard1/BRAD-Video.git
```

**Backend (python)**
1. Activate `BRAD-DEV` or `BRAD-1` conda environment used for developing the main `BRAD` repository
2. `pip install scrapetube`
3. `pip install youtube_transcript_api`

**Frontend (javascript)**
Run the following set of commands from the root of this repository.
```
curl -o- https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash
source ~/.nvm/nvm.sh
nvm install 20.18.0
nvm use 20.18.0
npm install --prefix ./brad-chat
```

### Build the RAG Database

To build the RAG database:
```
python youtube_database_construction.py
```

## Turn On

## Modifications

1. specify the youtube channel
2. specify the videos (we should add a new argument for this)

## Cite As
```
@article{pickard2024language,
  title={Language Model Powered Digital Biology with BRAD},
  author={Pickard, Joshua and Prakash, Ram and Choi, Marc Andrew and Oliven, Natalie and
          Stansbury, Cooper and Cwycyshyn, Jillian
          and Gorodetsky, Alex and Velasquez, Alvaro and Rajapakse, Indika},
  journal={arXiv preprint arXiv:2409.02864},
  url={https://arxiv.org/abs/2409.02864},
  year={2024}
}
```
