#This program takes the input tuple and class labels and produces the modified augmented input that can be given to Seq2Seq generator systems

def augmenter(inp, label):
	
	inp = inp.strip()
	label = label.strip()
	if "NULL" in label:
		nl = label.replace("NULL","").replace("_"," ").strip()
		tmp = inp.split(" ")
		out = tmp[0]+" NULL "+" ".join(tmp[2:])+" "+nl
	else:
		out = inp+" "+label.replace("_"," ")
	return out

if __name__ =="__main__":
	inp = "ORG locate GPE"
	label = "IS_PREP"
	
	print(augmenter(inp,label))
	
	inp = "ORG type ORG"
	label = "NULL_IS_PREP"
	
	print(augmenter(inp,label))
	
