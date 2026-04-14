
```bash
sudo apt-get install xclip

cat file | xclip # Copy only to `X` clipboard
cat file | xclip -selection clipboard # Copy to global clipboard
xclip -o # Print clipboard content to STDOUT
```

Consider creating an alias:

```bash
alias "cx=xclip"
alias "c=xclip -selection clipboard"
alias "v=xclip -o"
```
To see how useful this is, imagine I want to open my current path in a new terminal window (there may be other ways of doing it like Ctrl+T on some systems, but this is just for illustration purposes):

```bash
# Terminal 1:
pwd | cx

# Terminal 2:
cd `v`
```
Notice the ` ` around v. This executes v as a command first and then substitutes it in-place for cd to use