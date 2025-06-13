# Aliyun WAN2.1 Video Generation API

A Python script for batch video generation using Alibaba Cloud's WAN2.1 text-to-video models through their DashScope API.

## Features

- **Batch Processing**: Generate videos from multiple text prompts automatically
- **Multiple Models**: Support for both `wan2.1-t2v-turbo` and `wan2.1-t2v-plus` models
- **Async Task Management**: Submit tasks and poll for completion with configurable timeouts
- **Automatic Downloads**: Download generated videos to local storage
- **Progress Tracking**: CSV mapping file to track prompts and generated videos
- **Error Handling**: Robust error handling with timeout and failure detection

## Prerequisites

- Python 3.6+
- Aliyun API key with access to DashScope video generation services
- Required Python packages (see Installation)

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd aliyun_wan21_api
```

2. Install required dependencies:
```bash
pip install requests python-dotenv
```

3. Create a `.env` file in the project root:
```bash
touch .env
```

4. Add your Aliyun API key to the `.env` file:
```
ALIYUN_VIDEO_API=your_aliyun_api_key_here
```

## Setup

1. **Create prompts file**: Create a `prompts.txt` file with one prompt per line:
```
A beautiful sunset over the ocean with waves crashing
A cat playing with a ball of yarn in slow motion
Urban cityscape at night with neon lights
```

2. **Configure paths**: Update the file paths in `main.py` if needed:
   - `MAPPING_CSV`: Path for the CSV tracking file
   - Prompts file path in the `main()` function
   - Videos directory path in `download_video()` function

## Usage

Run the script to start batch video generation:

```bash
python main.py
```

The script will:
1. Read all prompts from `prompts.txt`
2. For each prompt, submit tasks to both WAN2.1 models
3. Wait for task completion (with 2-minute initial wait for plus model)
4. Download generated videos to the `videos/` directory
5. Record mappings in `prompt_video_mapping.csv`

## Configuration

### Models
- `wan2.1-t2v-turbo`: Faster generation, good quality
- `wan2.1-t2v-plus`: Higher quality, longer processing time

### Video Parameters
- **Size**: 720×1280 (portrait format)
- **Duration**: 5 seconds
- **Format**: MP4

### Timing
- **Poll Interval**: 20 seconds between status checks
- **Timeout**: 600 seconds (10 minutes) maximum wait time
- **Plus Model Delay**: 2-minute wait before polling for wan2.1-t2v-plus

## File Structure

```
aliyun_wan21_api/
├── main.py                     # Main script
├── prompts.txt                 # Input prompts file
├── .env                        # Environment variables (API key)
├── .gitignore                  # Git ignore rules
├── videos/                     # Downloaded video files
│   └── {model}_{task_id}.mp4
└── prompt_video_mapping.csv    # Tracking CSV file
```

## Output Files

### Videos
Generated videos are saved as: `{model}_{task_id}.mp4`
- Example: `wan2.1-t2v-turbo_12345abcde.mp4`

### Mapping CSV
The `prompt_video_mapping.csv` file contains:
| Column | Description |
|--------|-------------|
| model | Model used for generation |
| task_id | Unique task identifier |
| prompt | Original text prompt |
| filename | Path to downloaded video file |

## Error Handling

The script handles various error conditions:
- **API Errors**: HTTP errors are raised and displayed
- **Task Failures**: Failed or cancelled tasks throw RuntimeError
- **Timeouts**: Tasks exceeding timeout limit throw TimeoutError
- **Network Issues**: Download failures are handled gracefully

## API Rate Limits

Be mindful of Aliyun's API rate limits:
- Consider adding delays between submissions for large batches
- Monitor your API usage and quotas
- The script includes built-in delays for the plus model

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify your API key in the `.env` file
   - Ensure your Aliyun account has video generation permissions

2. **Path Errors**
   - Update hardcoded paths in the script to match your system
   - Ensure the `videos/` directory can be created

3. **Timeout Issues**
   - Increase the timeout parameter if needed
   - Check your internet connection
   - Verify API service status

### Debug Mode
Add print statements or logging to track progress:
```python
print(f"Processing prompt: {prompt}")
print(f"Task submitted: {task_id}")
```

## Security Notes

- Keep your `.env` file secure and never commit it to version control
- The `.gitignore` file excludes sensitive files by default
- Consider using environment variables in production deployments

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]

## Support

For API-related issues, consult the [Aliyun DashScope documentation](https://help.aliyun.com/zh/dashscope/).

For script issues, please open an issue in this repository.
