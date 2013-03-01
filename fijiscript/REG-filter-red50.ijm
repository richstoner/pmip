filename = getArgument();
filecomponents = split(filename,".j");
filebase = filecomponents[0];

output = filebase +"-c.jpg";

print('INPUT : ' + filename);
print('OUTPUT: ' + output);

open(filename);

// generate high contrast 
run("Find Edges");
run("Find Edges");
run("8-bit");

// normalize
run("Enhance Contrast", "saturated=50 normalize equalize");

// blur
run("Gaussian Blur...", "sigma=1.5");
setBackgroundColor(0,0,0);
run("Canvas Size...", "width=1000 height=750 position=Center zero"); 
//run("Size...", "width=1000 height=750 constrain average interpolation=Bilinear");

saveAs("jpg", output);
