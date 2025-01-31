# BRAD-Video RAG
This repository deploys a [`BRAD`](https://github.com/Jpickard1/BRAD) for Retrieval Augemented Generation (RAG) with videos from Youtube. A BRAD (Bioinformatics Retrieval Augmented Digital assistant) agent makes youtube channels searchable and interactive by both providing summary explinations and improving search in large video serieses. This repository contains every recorded seminar from the University of Michigan [Department of Computational Medicine and Bioinformatics (DCMB) youtube channel](https://www.youtube.com/@universityofmichigancomput8877/featured) and videos from 3Blue1Brown.

https://github.com/user-attachments/assets/293d7bf0-5e6b-4bcb-b62b-e4b8fd17e65f

**Note**: documentation is still under construction for this repository.

## Setup
Follow the below instructions to install the necessary dependencies and build the RAG database. This must be run one time when installing the system, and note that the dependencies identical to that of the [`BRAD` repository](https://github.com/Jpickard1/BRAD) with the addition of `scrapetube` and `youtube_transcript_api`.

### Install Dependencies

**Install BRAD**
This code must be run from the `video-rag` branch from the `BRAD` repository, and the roots of both repository must be located within the same directory. Run the below commands to install both repositories:
```
git clone https://github.com/Jpickard1/BRAD.git
git clone https://github.com/Jpickard1/BRAD-Video.git
```

**Backend (python)**
1. Activate `BRAD-DEV` or `BRAD-1` conda environment used for developing the `BRAD` according to the specifications of that [`repository.`](https://github.com/Jpickard1/BRAD)

If you wish to expand the library of searchable videos beyond those provided, install the following dependencies:

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

## Turn On
In separate terminals, execute the following commands from the root of this repository:
```
cd brad-chat
npm start
```

```
export OPENAI_API_KEY=<PLACE YOUR OPENAI API KEY HERE>
flask --app app run --host=0.0.0.0 --port=5000
```
**Note** Slight variations may be required if you are running this on windows or other systems.

### Build New Video RAG Databases from Youtube (optional)

To build the RAG database:
```
python youtube_database_construction.py
```

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
