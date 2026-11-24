# ----------------------------
# Makefile Options
# ----------------------------

NAME = BADAPPLE
DESCRIPTION = "bad apple"
COMPRESSED = NO
ARCHIVED = YES
HAS_PRINTF = NO

CFLAGS = -Wall -Wextra -Oz
CXXFLAGS = -Wall -Wextra -Oz

# ----------------------------

include $(shell cedev-config --makefile)
