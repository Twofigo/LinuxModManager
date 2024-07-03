# create a sample folder struture as a small playground for testing

rm -rf ./target
rm -rf ./mods

# setup target
mkdir -p ./target
mkdir -p ./target/A
mkdir -p ./target/B
mkdir -p ./target/C

# create files with some content
echo -n "target" > ./target/A/a.txt
echo -n "target" > ./target/B/b.txt
echo -n "target" > ./target/C/c.txt
echo -n "target" > ./target/d.txt

# setup mods
mkdir -p ./mods
cd ./mods

# source1
mkdir -p ./source1
mkdir -p ./source1/A
echo -n "source1" > ./source1/A/a.txt
echo -n "source1" > ./source1/c.txt
echo -n "source1" > ./source1/X.txt

# source2
mkdir -p ./source2
mkdir -p ./source2/A
mkdir -p ./source2/B
echo -n "source2" > ./source2/A/a.txt
echo -n "source2" > ./source2/B/b.txt
echo -n "source2" > ./source2/Y.txt

# source3
mkdir -p ./source3
mkdir -p ./source3/XYZ
echo -n "source3" > ./source3/XYZ/xyz.txt
echo -n "source3" > ./source3/Y.txt