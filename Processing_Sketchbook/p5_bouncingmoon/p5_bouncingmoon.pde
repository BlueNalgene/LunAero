int rad = 120;        // Width of the shape
float xpos, ypos;    // Starting position of shape    

float xspeed = 2.8;  // Speed of the shape
float yspeed = 2.2;  // Speed of the shape

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
  
  // Update the position of the shape
  xpos = xpos + ( xspeed * xdirection );
  ypos = ypos + ( yspeed * ydirection );
  
  // Test to see if the shape exceeds the boundaries of the screen
  // If it does, reverse its direction by multiplying by -1
  if (xpos > width || xpos < 0) {
    xdirection *= -1;
  }
  if (ypos > height-rad || ypos < 0) {
    ydirection *= -1;
  }

  // Draw the shape
  ellipse(xpos, ypos, rad, rad);
  
  //Saves a frame
  saveFrame("frames/fr-######.tif");
}