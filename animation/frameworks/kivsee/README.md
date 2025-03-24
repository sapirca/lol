'''
scp /Users/sapir/repos/lol/animation/songs/nikki.wav pi@10.0.0.45:/home/pi/Music/
'''

'''
brew install protobuf
pip install protobuf-to-pydantic
pip install mypy-protobuf

cd animation/frameworks/kivsee/scheme/
protoc --protobuf-to-pydantic_out=. effects.proto

export PATH="$PATH:/Users/sapir/miniconda3/envs/lol_agent/bin"
ls /Users/sapir/miniconda3/envs/lol_agent/bin/protoc-gen-protobuf-to-pydantic

'''
# Clone
git clone https://github.com/KivSee/kivsee-render.git
git clone https://github.com/KivSee/led-rings.git