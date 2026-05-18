import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


def change_brightness(image, value):
    value=int(value)
    if -255 <= value <= 255 :
        print("the value is valid")
        
        image = np.clip((image + value), 0, 255)

    else: 
        print("Invalid input. Please enter a number between -255 and 255 inclusive.")
        
    return image
  
def change_contrast(image, value):
    value=int(value)
    if -255 <= value <= 255 :
        print("the value is valid")
        factor = (259 * (value + 255)) / (255 * (259 - value))
        image1 = np.clip((factor * (image - 128)) + 128, 0, 255)
 
      
    else: 
        print("Invalid input. Please enter a number between -255 and 255 inclusive.")
    return image1
    
def apply_rectangle_selection(original_img, modified_img, mask):
    combined_img = original_img.copy()  

    for i in range(original_img.shape[0]):  
        for j in range(original_img.shape[1]):  
            if mask[i, j] == 1:  
                combined_img[i, j] = modified_img[i, j]  
    
    return combined_img
    
def grayscale(image):
    R = image[:, :, 0]
    G = image[:, :, 1]
    B = image[:, :, 2]
    grayscale = (0.3 * R + 0.59 * G + 0.11 * B)
    grayscale = np.clip(grayscale, 0, 255).astype(np.uint8)
    grayscaleimage = np.stack((grayscale, grayscale, grayscale), axis=-1)
    return grayscaleimage


  
    

def blur_effect(image):
    kernel = np.array([
        [0.0625, 0.125, 0.0625],
        [0.125, 0.25, 0.125],
        [0.0625, 0.125, 0.0625]
    ])
    
    blurred_image = image.copy()

    for channel in range(3): 
        for i in range(1, image.shape[0] - 1):
            for j in range(1, image.shape[1] - 1):
                region = image[i-1:i+2, j-1:j+2, channel]
                new_value = np.sum(region * kernel)
                blurred_image[i, j, channel] = np.clip(new_value, 0, 255)
    
    return blurred_image

def edge_detection(image):
    kernel = np.array([
        [-1, -1, -1],
        [-1, 8, -1],
        [-1, -1, -1]
    ])
    edge_image = image.copy()
    
    for channel in range(3): 
        for i in range(1, image.shape[0] - 1):
            for j in range(1, image.shape[1] - 1):
                region = image[i-1:i+2, j-1:j+2, channel]
                new_value = np.sum(region * kernel) + 128
                edge_image[i, j, channel] = np.clip(new_value, 0, 255)
    
    return edge_image

def embossed(image):
    kernel = np.array([
        [-1, -1, 0],
        [-1, 0, 1],
        [0, 1, 1]
    ])
    embossed_image = image.copy()
    
    for channel in range(3): 
        for i in range(1, image.shape[0] - 1):
            for j in range(1, image.shape[1] - 1):
                region = image[i-1:i+2, j-1:j+2, channel]
                new_value = np.sum(region * kernel) + 128
                embossed_image[i, j, channel] = np.clip(new_value, 0, 255)
    return embossed_image

def rectangle_select(image, x, y):
    r1, c1 = x
    r2, c2 = y
    r1, r2 = min(r1, r2), max(r1, r2)
    c1, c2 = min(c1, c2), max(c1, c2)
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    mask[r1:r2+1, c1:c2+1] = 1
    return mask

def magic_wand_select(image, x, thres):
    r,c = x
    r, c, thres = int(r), int(c), int(thres)
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    stack = [(r,c)]
    colour_chosen = image[c, r]
    
    while stack:
        cr, cc = stack.pop()
        r = (colour_chosen[0] + image[cc, cr][0]) / 2
        delta_red = colour_chosen[0] - image[cc, cr][0]
        delta_green = colour_chosen[1] - image[cc, cr][1]
        delta_blue = colour_chosen[2] - image[cc, cr][2]
        color_dist = np.sqrt((2 + r / 256) * delta_red**2 + 4 * delta_green**2 + (2 + (255 - r) / 256) * delta_blue**2)
        
        if color_dist <= thres and mask[cc, cr] == 0:
            mask[cc, cr] = 1
            for nr, nc in [(cr + 1, cc), (cr - 1, cc), (cr, cc + 1), (cr, cc - 1)]:
                if 0 <= nr < image.shape[1] and 0 <= nc < image.shape[0]:
                    stack.append((nr, nc))
        
    return mask


def compute_edge(mask):           
    rsize, csize = len(mask), len(mask[0]) 
    edge = np.zeros((rsize,csize))
    if np.all((mask == 1)): return edge        
    for r in range(rsize):
        for c in range(csize):
            if mask[r][c]!=0:
                if r==0 or c==0 or r==len(mask)-1 or c==len(mask[0])-1:
                    edge[r][c]=1
                    continue
                
                is_edge = False                
                for var in [(-1,0),(0,-1),(0,1),(1,0)]:
                    r_temp = r+var[0]
                    c_temp = c+var[1]
                    if 0<=r_temp<rsize and 0<=c_temp<csize:
                        if mask[r_temp][c_temp] == 0:
                            is_edge = True
                            break
    
                if is_edge == True:
                    edge[r][c]=1
            
    return edge

def save_image(filename, image):
    img = image.astype(np.uint8)
    mpimg.imsave(filename,img)

def load_image(filename):
    img = mpimg.imread(filename)
    if len(img[0][0])==4: # if png file
        img = np.delete(img, 3, 2)
    if type(img[0][0][0])==np.float32:  # if stored as float in [0,..,1] instead of integers in [0,..,255]
        img = img*255
        img = img.astype(np.uint8)
    mask = np.ones((len(img),len(img[0]))) # create a mask full of "1" of the same size of the laoded image
    img = img.astype(np.int32)
    return img, mask

def display_image(image, mask):
    # if using Spyder, please go to "Tools -> Preferences -> IPython console -> Graphics -> Graphics Backend" and select "inline"
    tmp_img = image.copy()
    edge = compute_edge(mask)
    for r in range(len(image)):
        for c in range(len(image[0])):
            if edge[r][c] == 1:
                tmp_img[r][c][0]=255
                tmp_img[r][c][1]=0
                tmp_img[r][c][2]=0
 
    plt.imshow(tmp_img)
    plt.axis('off')
    plt.show()
    print("Image size is",str(len(image)),"x",str(len(image[0])))

def menu():
    
    img = mask = np.array([])
  
       
if __name__ == "__main__":
    menu()

quit_program = False

while not quit_program:
 print("\nWhat do you want to do?")
 print("e - exit")
 print("l - load a picture")
    
 theirchoice = input("Your choice: ")

 if theirchoice == "e":
    print("program quit.")
    quit_program = True 


 elif theirchoice == "l": 
     myfile = input("Filename?: ")
     img, mask = load_image(myfile)
     display_image(img, mask)
        
     while not quit_program:
      print("\nWhat do you want to do?")
      print("e - exit")
      print("l - load a picture")
      print("s - save a picture")
      print("1 - adjust brightness")
      print("2 - adjust contrast")
      print("3 - apply grayscale")
      print("4 - apply blur")
      print("5 - edge detection")
      print("6 - emboss effect")
      print("7 - rectangle select")
      print("8 - magic wand select")

      secondchoice = input("Your choice: ")
            
      if secondchoice == "e":
        print("Exiting the program.")
        quit_program = True

      elif secondchoice == "l":
        myfile = input("Filename?: ")
        img, mask = load_image(myfile)
        display_image(img, mask)
        print("Image loaded.")

      elif secondchoice == "s":
        filename = input("Save as filename: ")
        save_image(filename, img)
        print ("saved")
        

      elif secondchoice == "1":
        print ("adjusting brightness")
        display_image(img, mask)
        brightnessvalue = input("Your new brightness value: ")
        modified_img = change_brightness(img, brightnessvalue) 
        img = apply_rectangle_selection(img, modified_img, mask)
        display_image(img, mask)
       
                                    
      elif secondchoice == "2":
        print ("adjusting contrast")
        print(img)
        display_image(img, mask)
        contrastvalue = input("Your new contrast value: ")
        modified_img = change_contrast(img, contrastvalue)
        img = apply_rectangle_selection(img, modified_img, mask)
        display_image(img, mask)
    
      elif secondchoice == "3":
        print ("adjusting grayscale")
        print(img)
        display_image(img, mask)
        modified_img = grayscale(img)
        img = apply_rectangle_selection(img, modified_img, mask)
        display_image(img, mask)
                    
      elif secondchoice == "4":
        modified_img = blur_effect(img)
        img = apply_rectangle_selection(img, modified_img, mask)
        display_image(img, mask)
        print("Blur effect applied.")
                    
      elif secondchoice == "5":
        modified_img = edge_detection(img)
        img = apply_rectangle_selection(img, modified_img, mask)
        display_image(img, mask)
        print("Edge detection applied.")
                    
      elif secondchoice == "6":
        modified_img = embossed(img)
        img = apply_rectangle_selection(img, modified_img, mask)
        display_image(img, mask)
        print("Emboss effect applied.")    
    
      elif secondchoice == "7":
        #Print the dimensions and valid coordinates
       print(f"The image dimensions consists of {img.shape[0]} rows and {img.shape[1]} columns")
       print(f"The range of valid row coordinates x are 0 to {img.shape[0]-1}")
       print(f"The range of valid column coordinates y are 0 to {img.shape[1]-1}")
      
       try:
         x = tuple(map(int, input("Enter top-left corner (row, col): ").split(',')))
         y = tuple(map(int, input("Enter bottom-right corner (row, col): ").split(',')))

        # Validate that coordinates are within image bounds and define a valid rectangle
         if (0 <= x[0] < img.shape[0] and 0 <= x[1] < img.shape[1] and
            0 <= y[0] < img.shape[0] and 0 <= y[1] < img.shape[1] and
            x[0] <= y[0] and x[1] <= y[1]):
               
            mask = rectangle_select(img, x, y)
            display_image(img,mask)
            print ("rectangle selected")
            
         else:
            print("Invalid coordinates. Please select valid coordinates.")
            
       except ValueError:
          print("Invalid input format. Please enter coordinates as 'row,col'.")
       
    
      elif secondchoice == "8":
       height, width, _ = img.shape
       print(f"The image dimensions are {height} (height) x {width} (width).")
       print(f" r coordinate should be between 0 and {width - 1}")
       print(f" c coordinate should be between 0 and {height - 1}")
 
       while True:
         try:
            r = int(input("Enter a valid r value: "))
            c = int(input("Enter a valid c value: "))
            threshold = int(input("Enter threshold value: "))
            x = [r, c]
            if 0 <= r < width and 0 <= c < height:
                break
            else:
                print("Please enter values within the range 0 <= r < {width} and 0 <= c < {height}.")
         except ValueError:
            print("Please enter valid integer values for r, c, and threshold.")
         
  
       mask = magic_wand_select(img, x, threshold)
       display_image(img, mask)
       print("Magic wand selection applied.")
        
      else:
         print("Invalid choice. Please select a valid option.")
            
 else:
    print("Invalid input. Please choose 'e' or 'l'")           

        
        
            
        



