import logging
from pathlib import Path
import SimpleITK as sitk
from platipy.imaging import ImageVisualiser

logger = logging.getLogger(__name__)


class VisualiseData:
    """
    Class that facilitates the visualisation of the data once converted

    Args:
        output_directory (str|pathlib.Path, optional): Directory in which converted data is stored.
            Defaults to ".".
    """

    def __init__(self, output_directory="."):
        self.output_directory = Path(output_directory)

    def visualise(self):
        """
        Function to visualise the data
        """

        # first stage: visualise each image individually
        for img_filename in self.output_directory.glob("**/images/*.nii.gz"):

            img = sitk.ReadImage(str(img_filename))

            vis = ImageVisualiser(img)
            fig = vis.show()

            # save image alongside nifti
            vis_filename = img_filename.parent / img_filename.name.replace(
                "".join(img_filename.suffixes), ".png"
            )
            fig.savefig(
                vis_filename,
                dpi=fig.dpi,
            )

            logger.debug("created visualisation%s", vis_filename)

        # Next visualise the structures on top of their linked image
        for struct_dir in self.output_directory.glob("**/structures/*"):

            # Make sure this is a structure directory
            if not struct_dir.is_dir():
                continue

            img_id = struct_dir.name.split("_")[1]

            img_links = list(struct_dir.parent.parent.glob(f"images/*{img_id}.nii.gz"))

            # If we have multiple linked images (not sure if this can happen but it might?) then
            # take the first one. If we find no linked images log and error and don't visualise for
            # now
            if len(img_links) == 0:
                logger.error("Linked image %s not found", img_id)
                continue

            img_file = img_links[0]

            img = sitk.ReadImage(str(img_file))

            vis = ImageVisualiser(img)
            masks = {
                f.name.replace(".nii.gz", ""): sitk.ReadImage(str(f))
                for f in struct_dir.glob("*.nii.gz")
            }

            if len(masks) == 0:
                logger.warning("No contours found in structure directory: %s", {struct_dir})
                continue

            vis.add_contour(masks)
            fig = vis.show()

            # save image inside structure directory
            vis_filename = struct_dir.parent.joinpath(f"{struct_dir.name}.png")
            fig.savefig(
                vis_filename,
                dpi=fig.dpi,
            )

            logger.debug("created visualisation%s", vis_filename)