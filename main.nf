params.imgdir = "assets/jpg"
Channel.fromPath("${params.imgdir}/*/*.jpg").into { input_imgs; input_imgs2 }
// params.imgdir = "example_images/"
// Channel.fromPath("${params.imgdir}/*.jpg").into { input_imgs; input_imgs2 }
// input_imgs2.println()

process img2rgb {
    echo true
    maxForks 4
    input:
    file(img) from input_imgs

    output:
    file("${output_file}") into img_rgbs

    script:
    output_file = "img.rgb.hsv.csv"
    """
    set -x
    img2rgb.py "${img}" -o "${output_file}"
    """
}
img_rgbs.collectFile(name: "img.rgb.hsv.csv", storeDir:"output")
