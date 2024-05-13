import re
import sys
from echo360.main import main
import fire

if __name__ == "__main__":
    # sys.argv[0] = re.sub(r"(-script\.pyw|\.exe)?$", "", sys.argv[0])
    # sys.exit(main())
    fire.Fire(main)
