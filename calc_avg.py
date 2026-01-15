import csv

def main():
    csv_file = '/Users/dohyeonkim/Documents/Documents - MacBook Pro dk/00_Projects/스프린트/gemini_prompt_test/source/scripts.csv'
    
    lengths_0 = []
    lengths_1 = []
    
    with open(csv_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            is_hoax = int(row['isHoax'])
            script = row['script']
            length = len(script)
            
            if is_hoax == 0:
                lengths_0.append(length)
            elif is_hoax == 1:
                lengths_1.append(length)
                
    avg_0 = sum(lengths_0) / len(lengths_0) if lengths_0 else 0
    avg_1 = sum(lengths_1) / len(lengths_1) if lengths_1 else 0
    
    print(f"isHoax=0 Average Length: {avg_0:.2f}")
    print(f"isHoax=1 Average Length: {avg_1:.2f}")

if __name__ == "__main__":
    main()
