import boto3
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from io import BytesIO

def detect_labels(photo, bucket, region_name="us-east-1"):
    client = boto3.client('rekognition', region_name=region_name)

    # Download the image from S3 first
    s3 = boto3.client('s3', region_name=region_name)
    s3_response = s3.get_object(Bucket=bucket, Key=photo)
    img_data = s3_response['Body'].read()

    # Pass image bytes directly to Rekognition (avoids bucket policy issues)
    response = client.detect_labels(
        Image={'Bytes': img_data},
        MaxLabels=50,
        MinConfidence=70)  # Only return labels with >= 70% confidence

    print('Detected labels for ' + photo) 
    print()   

    # Print label information
    for label in response['Labels']:
        print("Label:", label['Name'])
        print("Confidence:", label['Confidence'])
        print()

    # Load the image for display
    img = Image.open(BytesIO(img_data))

    # Display the image
    plt.imshow(img)
    ax = plt.gca()

    # Plot bounding boxes
    for label in response['Labels']:
        for instance in label.get('Instances', []):
            bbox = instance['BoundingBox']
            left = bbox['Left'] * img.width
            top = bbox['Top'] * img.height
            width = bbox['Width'] * img.width
            height = bbox['Height'] * img.height

            rect = patches.Rectangle((left, top), width, height, linewidth=1, edgecolor='r', facecolor='none')
            ax.add_patch(rect)

            label_text = label['Name'] + ' (' + str(round(label['Confidence'], 2)) + '%)'
            plt.text(left, top - 2, label_text, color='r', fontsize=8, bbox=dict(facecolor='white', alpha=0.7))

    plt.show()

    return len(response['Labels'])

def main():
    photo = '75ed01cb-63a3-457f-91b9-95133fe7f597.png'
    bucket = 'image-labeler-project'
    # Adjust this region to match the actual bucket region (e.g., us-east-1 or ap-south-1)
    region = 'us-east-1'
    label_count = detect_labels(photo, bucket, region_name=region)
    print("Labels detected:", label_count)

if __name__ == "__main__":
    main()