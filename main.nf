params.imgdir = "assets/jpg"
params.ignorePixels = "ignore-pixels.jpg"
params.outputDir = "output"
Channel.fromPath("${params.imgdir}/*/*.jpg").into { input_imgs; input_imgs2 }
// params.imgdir = "example_images/"
// Channel.fromPath("${params.imgdir}/*.jpg").into { input_imgs; input_imgs2 }
// input_imgs2.println()

Channel.fromPath("${params.ignorePixels}").set { ignore_pixels_ch }

process ignore_pixels {
    publishDir "${params.outputDir}", mode: 'copy'

    input:
    file(img) from ignore_pixels_ch

    output:
    file("${output_file}") into ignore_pixels_file

    script:
    output_file = "ignore_pixels.csv"
    """
    img2rgb.py "${img}" -o "${output_file}"
    """
}

process img2avg_rgb {
    echo true
    maxForks 4
    input:
    set file(img), file(ignore_file) from input_imgs.combine(ignore_pixels_file)

    output:
    file("${output_file}") into img_rgbs

    script:
    output_file = "img.rgb.hsv.csv"
    """
    img2avg-rgb.py "${img}" -o "${output_file}"
    """
}
img_rgbs.collectFile(name: "img.rgb.hsv.csv", storeDir:"${params.outputDir}")
