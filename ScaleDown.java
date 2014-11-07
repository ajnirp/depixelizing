import java.io.File;
import javax.imageio.ImageIO;
import java.io.IOException;
import java.awt.image.BufferedImage;

public class ScaleDown {
  public static void main(String[] args) {
    try {
      int scalingFactor = Integer.parseInt(args[1]);
      int scalingFactorSqr = scalingFactor*scalingFactor;
      BufferedImage input = ImageIO.read(new File(args[0]));
      int height = input.getHeight();
      int width = input.getWidth();
      BufferedImage output = new BufferedImage(height/scalingFactor, width/scalingFactor, input.getType());
      for (int i = 0; i < height; i += scalingFactor) {
        for (int j = 0; j < width; j += scalingFactor) {
          int red = 0, green = 0, blue = 0;
          for (int ii = i; ii < i+scalingFactor; ii++) {
            for (int jj = j; jj < j+scalingFactor; jj++) {
              int color = input.getRGB(jj, ii);
              red += (color & 0x00ff0000) >> 16;
              green += (color & 0x0000ff00) >> 8;
              blue += (color & 0x000000ff);
            }
          }
          red /= scalingFactorSqr;
          green /= scalingFactorSqr;
          blue /= scalingFactorSqr;
          int x = j/scalingFactor;
          int y = i/scalingFactor;
          output.setRGB(x, y, (red << 16) + (green << 8) + blue);
        }
      }
      ImageIO.write(output, "png", new File(args[2]));
    }
    catch (IOException e) {
      e.printStackTrace();
    }
  }
}