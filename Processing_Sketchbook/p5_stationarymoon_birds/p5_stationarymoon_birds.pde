int rad = 220;        // Width of the shape
int birad = 0;        // Radius of bird
int bird = 0;         // Bird counter
float xbird, ybird, dirbird; //movement of bird
float xpos, ypos;    // Starting position of shape    
int i = 0;

float xspeed = 5.6;  // Speed of the shape
float yspeed = 4.4;  // Speed of the shape

int xdirection = int(random(-5, 5));  // Left or Right
int ydirection = int(random(-5, 5));  // Top to Bottom


void setup() {
  
  size(800, 600);
  noStroke();
  frameRate(30);
  ellipseMode(RADIUS);
  // Set the starting position of the shape
  xpos = width/2;
  ypos = height/2;
}

void draw() 
{
  background(0);
  
  if (bird == 0) {
    fill(255);
    ellipse(xpos, ypos, rad, rad);
    birad = int(random(2,80));
    xbird = int(random(10,790));
    ybird = -sq((xbird/20) - (width/40)) + height;
    if (xbird < 400) {
      dirbird = 1;
    }
    fill(50);
    ellipse(xbird, ybird, birad, birad);
    bird = 1;
  }
  else {
    if (i < 100) {
      fill(255);
      ellipse(xpos, ypos, rad, rad);
      xbird = xbird - xspeed;
      ybird = ybird - yspeed;
      fill(50);
      ellipse(xbird, ybird, birad, birad);
      i++;
    }
    else {
      i = 0;
      bird = 0;
    }
  }
    
  
  
  // Update the position of the shape
  //xpos = xpos + ( xspeed * xdirection );
  //ypos = ypos + ( yspeed * ydirection );
  
  
  
  

  // Draw the shape
  //ellipse(xpos, ypos, rad, rad);
  
  //Saves a frame
  saveFrame("frames/fr-######.tif");
}