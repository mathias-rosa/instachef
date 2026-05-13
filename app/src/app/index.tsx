import { View } from "react-native";
import { Button, Text } from "heroui-native";

export default function Index() {
  return (
    <View className="flex-1 bg-background p-safe">
      <View className="w-full items-center py-4">
        <Text.Heading>Instachef</Text.Heading>
      </View>
      <View className="flex-1 justify-center items-center ">
        <Button onPress={() => console.log("Pressed!")}>Get Started</Button>
      </View>
    </View>
  );
}
