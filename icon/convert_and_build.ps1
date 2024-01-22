$i = 57
while($i -le 63) {
  convert ico/$i.ico png/$i.png
  $i++
}
convert png/57.png png/58.png png/59.png png/60.png png/61.png png/62.png png/63.png -colors 256 program.ico